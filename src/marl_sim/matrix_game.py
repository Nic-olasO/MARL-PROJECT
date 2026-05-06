from __future__ import annotations

from dataclasses import dataclass
from random import Random


Action = int


@dataclass(frozen=True)
class StepResult:
    observations: dict[str, tuple[int, ...]]
    rewards: dict[str, float]
    terminated: bool
    info: dict[str, str]


class CoordinationGame:
    """Tiny two-agent coordination game for dependency-light smoke tests."""

    agents = ("agent_0", "agent_1")

    def __init__(self, horizon: int = 8, seed: int = 7) -> None:
        self.horizon = horizon
        self._rng = Random(seed)
        self._step = 0
        self._last_actions = (0, 0)

    def reset(self, seed: int | None = None) -> dict[str, tuple[int, ...]]:
        if seed is not None:
            self._rng.seed(seed)
        self._step = 0
        self._last_actions = (0, 0)
        return self._observations()

    def sample_action(self) -> Action:
        return self._rng.randrange(2)

    def step(self, actions: dict[str, Action]) -> StepResult:
        if self._step >= self.horizon:
            raise RuntimeError("Episode has terminated. Call reset() before stepping again.")

        a0 = actions["agent_0"]
        a1 = actions["agent_1"]
        if a0 not in (0, 1) or a1 not in (0, 1):
            raise ValueError("CoordinationGame actions must be 0 or 1.")

        coordinated = a0 == a1
        unsafe_collision = a0 == 1 and a1 == 1
        reward = 1.0 if coordinated else -0.25
        if unsafe_collision:
            reward -= 0.5

        self._last_actions = (a0, a1)
        self._step += 1

        return StepResult(
            observations=self._observations(),
            rewards={"agent_0": reward, "agent_1": reward},
            terminated=self._step >= self.horizon,
            info={"event": "unsafe_collision" if unsafe_collision else "ok"},
        )

    def _observations(self) -> dict[str, tuple[int, ...]]:
        remaining = self.horizon - self._step
        obs = (*self._last_actions, remaining)
        return {"agent_0": obs, "agent_1": obs}
