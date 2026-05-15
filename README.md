# MARL Project

First MARL project for NPS.

This repository now combines two complementary tracks:

- `src/marl_sim`: dependency-light smoke tests, including a matrix
  coordination game and PettingZoo Tic-Tac-Toe check.
- `src/marl_practice`: a PettingZoo `ParallelEnv` task-allocation simulator
  with RLlib registration helpers, tests, Hydra config, and research tracking.

## Docker Simulation Environment

Build and run the lean MARL smoke-test sandbox:

```powershell
docker compose up --build
```

Run the explicit PettingZoo smoke service:

```powershell
docker compose run --rm pettingzoo
```

Run an interactive shell in the container:

```powershell
docker compose run --rm marl bash
```

The default command runs a small PettingZoo Tic-Tac-Toe smoke simulation from
`src/marl_sim/smoke_pettingzoo.py`. This gives us a quick check that the core
multi-agent simulation stack is installed before we add larger benchmarks or
training algorithms.

Run additional local checks:

```powershell
docker compose run --rm pettingzoo
docker compose run --rm matrix
docker compose run --rm task-demo
docker compose run --rm drone-demo
docker compose run --rm test
```

## Drone Simulation and Video

`DroneSearchEnv` is a small PettingZoo `ParallelEnv` for multi-drone target
search. It models drones on a 2D grid, active targets, no-fly zones, collisions,
and safety counters. The first renderer intentionally produces a simple animated
GIF so backend experiments can hand the UI a concrete artifact without requiring
a browser or 3D engine.

Generate a local demo trace and video:

```powershell
docker compose run --rm drone-demo
```

Outputs:

- `runs/drone_demo.gif`
- `runs/drone_demo_trace.json`

## Task-Allocation Simulation

`TaskAllocationEnv` is a small PettingZoo `ParallelEnv` where multiple agents
move on a 2D grid and complete active tasks. It is intentionally simple so it
can become the baseline target for IPPO/MAPPO, QMIX, VDN, and reward-shaping
experiments.

Key files:

- `src/marl_practice/envs/task_allocation_env.py`: simulator implementation.
- `src/marl_practice/training/rllib_env.py`: optional RLlib wrapper and
  registration helper.
- `configs/ippo_task_allocation.yaml`: first IPPO-style training config.
- `src/marl_practice/baselines/`: random and greedy scripted baselines.
- `src/marl_practice/logging/`: JSONL episode logging helpers.
- `tests/`: API, config, and wrapper smoke tests.

Run a baseline episode and append the result to JSONL:

```powershell
python -m marl_practice.baselines --policy greedy --seed 7 --log-path runs/baselines.jsonl
```

Episode records include return, completed tasks, completion rate, per-agent
returns, and safety summaries such as invalid serves and collision counts.

## Dashboard

Start the local dashboard after logging one or more baseline episodes:

```bash
python -m marl_practice.dashboard --log-path runs/baselines.jsonl
```

Then open `http://127.0.0.1:8000`. The dashboard reads JSONL episode records
and shows returns, completion rates, safety violations, policy filters, and
recent runs.

Docker users can run the same UI with:

```bash
docker compose run --rm --service-ports dashboard
```

## Research Tracking

Use `docs/research/README.md` to track the literature matrix, paper notes, and
implementation questions. `MARL-Papers/` stores the larger paper collection
from this repository.

Project updates are tracked in `CHANGELOG.md`.

## GitHub Pull Agent

Use the local pull watcher when multiple people or tools are pushing to GitHub:

```powershell
.\scripts\github_pull_agent.ps1 -PollSeconds 60
```

It checks the current branch's upstream, skips unsafe pulls when your worktree
has local changes, and only pulls with `--ff-only`. More details live in
`docs/github_pull_agent.md`.

## Notes

- `requirements.txt` tracks the broader research stack.
- `requirements-docker.txt` is intentionally minimal: NumPy, Gymnasium, and
  PettingZoo classic environments plus pytest for smoke tests.
- `requirements-marl.txt` captures the fuller stack from the task-allocation
  scaffold.
- Heavier tooling such as Torch, SciPy, TensorBoard, SuperSuit, RLlib,
  BenchMARL, MuJoCo, or simulator-specific SDKs can be installed locally from
  the broader requirements first, then promoted into a heavier Docker target
  once the target training stack is chosen.

## Update Log

Use this section to track visible GitHub repository progress.

### 2026-05-05

- Added a lean Docker scaffold for running MARL smoke simulations.
- Added a dependency-light matrix coordination game for fast local checks.
- Added a PettingZoo smoke simulation target for the first external MARL API.
- Added research notes summarizing safe MARL and LLM-agent interaction-reward papers.
- Added planning docs for simulation milestones, metrics, and future paper notes.
