from __future__ import annotations

import subprocess

from scripts.github_pull_agent import sync_if_behind


def git(repository, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=repository,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def commit_file(repository, filename: str, content: str, message: str) -> None:
    path = repository / filename
    path.write_text(content, encoding="utf-8")
    git(repository, "add", filename)
    git(
        repository,
        "-c",
        "user.name=Test",
        "-c",
        "user.email=test@example.com",
        "commit",
        "-m",
        message,
    )


def test_sync_if_behind_fast_forwards_clean_worktree(tmp_path):
    remote = tmp_path / "remote.git"
    seed = tmp_path / "seed"
    local = tmp_path / "local"
    other = tmp_path / "other"

    git(tmp_path, "init", "--bare", str(remote))
    git(tmp_path, "clone", str(remote), str(seed))
    commit_file(seed, "README.md", "initial\n", "initial")
    git(seed, "branch", "-M", "main")
    git(seed, "push", "-u", "origin", "main")

    git(tmp_path, "clone", str(remote), str(local))
    git(tmp_path, "clone", str(remote), str(other))
    git(local, "checkout", "-b", "feature/sync-agent")
    git(local, "push", "-u", "origin", "feature/sync-agent")
    git(other, "fetch", "origin")
    git(other, "checkout", "feature/sync-agent")
    commit_file(other, "new.txt", "remote update\n", "remote update")
    git(other, "push", "origin", "feature/sync-agent")

    result = sync_if_behind(local, tmp_path / "agent.log")

    assert result == "Pulled 1 new commit(s)."
    assert (local / "new.txt").read_text(encoding="utf-8") == "remote update\n"


def test_sync_if_behind_skips_dirty_worktree(tmp_path):
    remote = tmp_path / "remote.git"
    seed = tmp_path / "seed"
    local = tmp_path / "local"
    other = tmp_path / "other"

    git(tmp_path, "init", "--bare", str(remote))
    git(tmp_path, "clone", str(remote), str(seed))
    commit_file(seed, "README.md", "initial\n", "initial")
    git(seed, "branch", "-M", "main")
    git(seed, "push", "-u", "origin", "main")

    git(tmp_path, "clone", str(remote), str(local))
    git(tmp_path, "clone", str(remote), str(other))
    commit_file(other, "new.txt", "remote update\n", "remote update")
    git(other, "push", "origin", "main")
    (local / "local.txt").write_text("local change\n", encoding="utf-8")

    result = sync_if_behind(local, tmp_path / "agent.log", "origin", "main")

    assert result == "Skipped pull: worktree has local changes."
    assert not (local / "new.txt").exists()
