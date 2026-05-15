# Marlowe: GitHub Pull Agent

Marlowe is a local watcher that checks GitHub for new commits and pulls them
only when it is safe to do so.

Run one check:

```powershell
.\scripts\github_pull_agent.ps1 -Once
```

Run continuously:

```powershell
.\scripts\github_pull_agent.ps1 -PollSeconds 60
```

Marlowe:

- fetches `origin/main`;
- pulls with `--ff-only` when the local branch is clean and behind;
- skips pulling when local files have changes;
- skips pulling when local and remote history diverge;
- writes logs to `.tmp/github-pull-agent.log`.

PDF research files remain local-only because `*.pdf` is ignored and the
repository has Paperlock, a pre-push/GitHub Actions guard against tracked PDFs.
