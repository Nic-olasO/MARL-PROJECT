# MARL Project

First MARL project for NPS.

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

## Notes

- `requirements.txt` tracks the broader research stack.
- `requirements-docker.txt` is intentionally minimal: NumPy, Gymnasium, and
  PettingZoo classic environments only.
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
