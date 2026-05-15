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
docker compose run --rm matrix
docker compose run --rm task-demo
docker compose run --rm test
```

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

## Research Tracking

Use `docs/research/README.md` to track the literature matrix, paper notes, and
implementation questions. `MARL-Papers/` stores the larger paper collection
from this repository.

Project updates are tracked in `CHANGELOG.md`.

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
