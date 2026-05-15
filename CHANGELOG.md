# Changelog

All notable updates to this MARL simulation repository will be tracked here.

## 2026-05-05

- Added a cross-platform Python GitHub pull agent for monitoring and safe fast-forward pulls.
- Added JSONL episode logging, random/scripted task-allocation baselines, and safety violation summaries.
- Added a larger paper batch to the research matrix, covering Markov games, early cooperative MARL, game-theoretic learning, deep MARL stability, safe MARL, mean-field MARL, and LLM-based multi-agent systems.
- Added research-tracking docs for the literature matrix, paper notes, and open research questions.
- Extended `TaskAllocationEnv` with configurable reward modes, view radius, and richer metrics.
- Added initial RLlib/IPPO environment registration and Hydra-compatible config scaffolding.
- Added GitHub Actions CI and explicit Docker Compose `test`/`demo` services.
- Added Docker support with `Dockerfile`, `docker-compose.yml`, and `.dockerignore`.
- Added a starter PettingZoo `ParallelEnv` for cooperative task allocation.
- Added smoke tests for the environment API and observation/step behavior.
- Updated local activation script to include `PYTHONPATH`.
- Verified the stack locally and inside Docker.

## 2026-04-30

- Created the initial Python 3.12 virtual environment.
- Added `requirements-marl.txt` for the MARL software stack.
- Added `activate_marl.sh` for local development setup.
- Added `.gitignore` to avoid committing virtual environments, caches, experiment outputs, and local research PDFs.
