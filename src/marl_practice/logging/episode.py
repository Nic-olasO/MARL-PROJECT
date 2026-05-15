from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class EpisodeRecord:
    """Serializable summary for one completed episode."""

    seed: int | None
    policy_name: str
    episode_return: float
    steps: int
    completed_tasks: int
    completion_rate: float
    safety_summary: dict[str, Any] | None = None
    per_agent_returns: dict[str, float] | None = None

    def to_dict(self) -> dict[str, Any]:
        return _to_jsonable(asdict(self))


def append_jsonl(path: str | Path, record: EpisodeRecord | dict[str, Any]) -> None:
    """Append one JSON-serializable record to a JSONL file."""

    jsonable_record = _record_to_dict(record)
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("a", encoding="utf-8") as file:
        json.dump(jsonable_record, file, sort_keys=True)
        file.write("\n")


def write_episode_record(path: str | Path, record: EpisodeRecord | dict[str, Any]) -> None:
    """Write one episode record as a JSONL line."""

    append_jsonl(path, record)


def read_episode_records(path: str | Path) -> list[dict[str, Any]]:
    """Read episode records from a JSONL file."""

    records: list[dict[str, Any]] = []
    with Path(path).open("r", encoding="utf-8") as file:
        for line in file:
            stripped = line.strip()
            if stripped:
                records.append(json.loads(stripped))
    return records


def _record_to_dict(record: EpisodeRecord | dict[str, Any]) -> dict[str, Any]:
    if isinstance(record, EpisodeRecord):
        return record.to_dict()
    return _to_jsonable(record)


def _to_jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _to_jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_to_jsonable(item) for item in value]
    if hasattr(value, "tolist"):
        return _to_jsonable(value.tolist())
    if hasattr(value, "item"):
        try:
            return value.item()
        except ValueError:
            pass
    return value
