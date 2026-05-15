from __future__ import annotations

import argparse
import datetime as dt
import subprocess
import time
from pathlib import Path


def run_git(repository: Path, *args: str) -> list[str]:
    result = subprocess.run(
        ["git", *args],
        cwd=repository,
        check=False,
        capture_output=True,
        text=True,
    )
    output = "\n".join(part for part in (result.stdout, result.stderr) if part)
    if result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {output.strip()}")
    return [line for line in output.splitlines() if line]


def first_line(lines: list[str]) -> str:
    return lines[0] if lines else ""


def optional_git(repository: Path, *args: str) -> str:
    try:
        return first_line(run_git(repository, *args))
    except RuntimeError:
        return ""


def current_branch(repository: Path) -> str:
    branch = first_line(run_git(repository, "symbolic-ref", "--quiet", "--short", "HEAD"))
    if not branch:
        raise RuntimeError("repository is not on a branch; detached HEAD is not supported")
    return branch


def watch_target(
    repository: Path,
    remote: str | None = None,
    branch: str | None = None,
) -> tuple[str, str, str]:
    local_branch = current_branch(repository)
    target_remote = remote or optional_git(
        repository, "config", "--get", f"branch.{local_branch}.remote"
    )
    target_branch = branch

    if not target_branch:
        merge_ref = optional_git(
            repository, "config", "--get", f"branch.{local_branch}.merge"
        )
        if merge_ref:
            target_branch = merge_ref.removeprefix("refs/heads/")

    if not target_remote or not target_branch:
        raise RuntimeError(
            f"current branch '{local_branch}' does not have an upstream; "
            "set one with 'git branch --set-upstream-to <remote>/<branch>' "
            "or pass --remote and --branch"
        )

    return local_branch, target_remote, target_branch


def write_log(log_path: Path, message: str) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    timestamp = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {message}"
    print(line, flush=True)
    with log_path.open("a", encoding="utf-8") as file:
        file.write(f"{line}\n")


def worktree_is_clean(repository: Path) -> bool:
    return not run_git(repository, "status", "--porcelain")


def ahead_behind(repository: Path, remote: str, branch: str) -> tuple[int, int]:
    counts = run_git(
        repository,
        "rev-list",
        "--left-right",
        "--count",
        f"HEAD...{remote}/{branch}",
    )
    ahead, behind = counts[0].split()
    return int(ahead), int(behind)


def sync_if_behind(
    repository: Path,
    log_path: Path,
    remote: str | None = None,
    branch: str | None = None,
) -> str:
    local_branch, target_remote, target_branch = watch_target(repository, remote, branch)
    write_log(
        log_path,
        f"Checking {target_remote}/{target_branch} for local branch {local_branch} "
        f"from {repository}",
    )
    run_git(repository, "fetch", "--prune", target_remote)

    if not worktree_is_clean(repository):
        message = "Skipped pull: worktree has local changes."
        write_log(log_path, message)
        return message

    ahead, behind = ahead_behind(repository, target_remote, target_branch)
    if behind == 0:
        message = f"Already up to date. Local ahead={ahead} behind={behind}."
        write_log(log_path, message)
        return message

    if ahead > 0:
        message = (
            f"Skipped pull: local branch is ahead by {ahead} and behind by {behind}. "
            "Manual rebase/merge needed."
        )
        write_log(log_path, message)
        return message

    write_log(log_path, f"Pulling {behind} new commit(s) with --ff-only.")
    for line in run_git(repository, "pull", "--ff-only", target_remote, target_branch):
        write_log(log_path, line)
    return f"Pulled {behind} new commit(s)."


def default_repository() -> Path:
    return Path(__file__).resolve().parents[1]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Monitor a GitHub branch and fast-forward pull when safe."
    )
    parser.add_argument("--repository", type=Path, default=default_repository())
    parser.add_argument(
        "--remote",
        default=None,
        help="Defaults to the current branch upstream remote.",
    )
    parser.add_argument(
        "--branch",
        default=None,
        help="Defaults to the current branch upstream branch.",
    )
    parser.add_argument("--poll-seconds", type=int, default=60)
    parser.add_argument(
        "--log-path",
        type=Path,
        default=None,
        help="Defaults to REPOSITORY/.tmp/github-pull-agent.log",
    )
    parser.add_argument("--once", action="store_true", help="Run one check and exit.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    repository = args.repository.resolve()
    log_path = args.log_path or repository / ".tmp" / "github-pull-agent.log"

    if args.poll_seconds < 1:
        raise ValueError("--poll-seconds must be at least 1")

    write_log(
        log_path,
        f"GitHub pull agent started. PollSeconds={args.poll_seconds} Once={args.once}",
    )

    try:
        while True:
            try:
                sync_if_behind(repository, log_path, args.remote, args.branch)
            except Exception as exc:
                write_log(log_path, f"Error: {exc}")

            if args.once:
                break
            time.sleep(args.poll_seconds)
    finally:
        write_log(log_path, "GitHub pull agent stopped.")


if __name__ == "__main__":
    main()
