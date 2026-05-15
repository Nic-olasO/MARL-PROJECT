# Marlowe: GitHub Pull Agent

Marlowe is a local watcher that checks GitHub for new commits and pulls them
only when it is safe to do so.

Run one check:

```bash
python scripts/github_pull_agent.py --once
```

```powershell
.\scripts\github_pull_agent.ps1 -Once
```

Run continuously:

```bash
python scripts/github_pull_agent.py --poll-seconds 60
```

```powershell
.\scripts\github_pull_agent.ps1 -PollSeconds 60
```

Marlowe:

- fetches the current branch's configured upstream remote;
- pulls with `--ff-only` when the local branch is clean and behind;
- skips pulling when local files have changes;
- skips pulling when local and remote history diverge;
- writes logs to `.tmp/github-pull-agent.log`.

By default, both scripts watch the upstream configured for the current branch
such as `origin/main`. To override that target explicitly:

```bash
python scripts/github_pull_agent.py --remote origin --branch main --once
```

```powershell
.\scripts\github_pull_agent.ps1 -Remote origin -Branch main -Once
```

On macOS, you can leave the Python agent running in a terminal while you work:

```bash
cd /Users/perla/Downloads/MARL-PROJECT
python scripts/github_pull_agent.py --poll-seconds 60
```

Stop it with `Ctrl+C`.

PDF research files remain local-only because `*.pdf` is ignored and the
repository has Paperlock, a pre-push/GitHub Actions guard against tracked PDFs.
