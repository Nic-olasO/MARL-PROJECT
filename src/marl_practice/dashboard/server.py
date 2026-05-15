from __future__ import annotations

import argparse
import json
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

from marl_practice.logging import read_episode_records


DEFAULT_LOG_PATH = Path("runs/baselines.jsonl")
STATIC_DIR = Path(__file__).resolve().parent / "static"


def load_dashboard_records(log_path: str | Path) -> list[dict[str, Any]]:
    path = Path(log_path)
    if not path.exists():
        return []
    return read_episode_records(path)


def summarize_records(records: list[dict[str, Any]]) -> dict[str, Any]:
    if not records:
        return {
            "episodes": 0,
            "avg_return": 0.0,
            "avg_completion_rate": 0.0,
            "total_completed_tasks": 0,
            "total_safety_violations": 0,
            "policies": [],
        }

    total_return = sum(float(record.get("episode_return", 0.0)) for record in records)
    total_completion = sum(float(record.get("completion_rate", 0.0)) for record in records)
    total_completed = sum(int(record.get("completed_tasks", 0)) for record in records)
    total_violations = sum(_total_violations(record) for record in records)
    policies = sorted({str(record.get("policy_name", "unknown")) for record in records})

    return {
        "episodes": len(records),
        "avg_return": total_return / len(records),
        "avg_completion_rate": total_completion / len(records),
        "total_completed_tasks": total_completed,
        "total_safety_violations": total_violations,
        "policies": policies,
    }


def dashboard_payload(log_path: str | Path) -> dict[str, Any]:
    records = load_dashboard_records(log_path)
    return {
        "log_path": str(log_path),
        "summary": summarize_records(records),
        "episodes": records,
    }


def _total_violations(record: dict[str, Any]) -> int:
    safety = record.get("safety_summary") or {}
    if "total_violations" in safety:
        return int(safety["total_violations"])
    if "total_invalid_serves" in safety:
        return int(safety["total_invalid_serves"])
    return int(safety.get("invalid_serves", 0)) + int(safety.get("collision_events", 0))


class DashboardRequestHandler(SimpleHTTPRequestHandler):
    server: "DashboardServer"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, directory=str(STATIC_DIR), **kwargs)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/episodes":
            self._handle_episode_api(parsed.query)
            return
        if parsed.path == "/health":
            self._send_json({"status": "ok"})
            return
        if parsed.path == "/":
            self.path = "/index.html"
        super().do_GET()

    def log_message(self, format: str, *args: Any) -> None:
        if not self.server.quiet:
            super().log_message(format, *args)

    def _handle_episode_api(self, query: str) -> None:
        params = parse_qs(query)
        log_path = params.get("path", [str(self.server.log_path)])[0]
        payload = dashboard_payload(log_path)
        self._send_json(payload)

    def _send_json(self, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, sort_keys=True).encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


class DashboardServer(ThreadingHTTPServer):
    def __init__(
        self,
        server_address: tuple[str, int],
        handler_class: type[DashboardRequestHandler],
        log_path: Path,
        quiet: bool = False,
    ) -> None:
        super().__init__(server_address, handler_class)
        self.log_path = log_path
        self.quiet = quiet


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Serve the local MARL dashboard.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--log-path", type=Path, default=DEFAULT_LOG_PATH)
    parser.add_argument("--quiet", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    server = DashboardServer(
        (args.host, args.port),
        DashboardRequestHandler,
        log_path=args.log_path,
        quiet=args.quiet,
    )
    print(f"Serving MARL dashboard at http://{args.host}:{args.port}")
    print(f"Reading episode log from {args.log_path}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nDashboard stopped.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
