from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
from gymnasium import spaces
from pettingzoo import ParallelEnv


@dataclass(frozen=True)
class Target:
    position: np.ndarray
    active: bool = True


class DroneSearchEnv(ParallelEnv):
    """Small grid drone environment for MARL experiments and visualization."""

    metadata = {"name": "drone_search_v0", "render_modes": ["ansi"]}

    ACTIONS = {
        0: np.array([0, 0], dtype=np.int32),
        1: np.array([0, 1], dtype=np.int32),
        2: np.array([0, -1], dtype=np.int32),
        3: np.array([-1, 0], dtype=np.int32),
        4: np.array([1, 0], dtype=np.int32),
    }

    def __init__(
        self,
        num_drones: int = 3,
        num_targets: int = 5,
        grid_size: int = 12,
        max_cycles: int = 80,
        num_no_fly_zones: int = 6,
        capture_radius: int = 0,
        render_mode: str | None = None,
    ) -> None:
        if num_drones < 1:
            raise ValueError("num_drones must be at least 1")
        if num_targets < 1:
            raise ValueError("num_targets must be at least 1")
        if grid_size < 4:
            raise ValueError("grid_size must be at least 4")
        if max_cycles < 1:
            raise ValueError("max_cycles must be at least 1")
        if num_no_fly_zones < 0:
            raise ValueError("num_no_fly_zones must be non-negative")
        if capture_radius < 0:
            raise ValueError("capture_radius must be non-negative")

        self.possible_agents = [f"drone_{idx}" for idx in range(num_drones)]
        self.num_targets = num_targets
        self.grid_size = grid_size
        self.max_cycles = max_cycles
        self.num_no_fly_zones = num_no_fly_zones
        self.capture_radius = capture_radius
        self.render_mode = render_mode

        self._action_spaces = {
            agent: spaces.Discrete(len(self.ACTIONS))
            for agent in self.possible_agents
        }
        self._observation_spaces = {
            agent: spaces.Box(low=0.0, high=1.0, shape=(8,), dtype=np.float32)
            for agent in self.possible_agents
        }

        self.agents: list[str] = []
        self.drone_positions: dict[str, np.ndarray] = {}
        self.targets: list[Target] = []
        self.no_fly_zones: set[tuple[int, int]] = set()
        self.steps = 0
        self.collision_events = 0
        self.no_fly_violations: dict[str, int] = {}
        self.target_captures: dict[str, int] = {}
        self.np_random = np.random.default_rng()

    def observation_space(self, agent: str) -> spaces.Box:
        return self._observation_spaces[agent]

    def action_space(self, agent: str) -> spaces.Discrete:
        return self._action_spaces[agent]

    def reset(self, seed: int | None = None, options: dict | None = None):
        del options
        self.np_random = np.random.default_rng(seed)
        self.agents = self.possible_agents[:]
        self.steps = 0
        self.collision_events = 0
        self.no_fly_violations = {agent: 0 for agent in self.possible_agents}
        self.target_captures = {agent: 0 for agent in self.possible_agents}

        occupied: set[tuple[int, int]] = set()
        self.drone_positions = {
            agent: self._sample_empty_cell(occupied)
            for agent in self.possible_agents
        }
        self.targets = [
            Target(position=self._sample_empty_cell(occupied), active=True)
            for _ in range(self.num_targets)
        ]
        self.no_fly_zones = {
            tuple(self._sample_empty_cell(occupied).tolist())
            for _ in range(self.num_no_fly_zones)
        }

        return self._observations(), self._infos()

    def step(self, actions: dict[str, int]):
        if not self.agents:
            return {}, {}, {}, {}, {}

        self.steps += 1
        rewards = {agent: -0.01 for agent in self.agents}

        for agent in self.agents:
            action = int(actions.get(agent, 0))
            move = self.ACTIONS.get(action, self.ACTIONS[0])
            next_position = self.drone_positions[agent] + move
            self.drone_positions[agent] = np.clip(next_position, 0, self.grid_size - 1)
            if tuple(self.drone_positions[agent].tolist()) in self.no_fly_zones:
                self.no_fly_violations[agent] += 1
                rewards[agent] -= 0.25

        collided_agents = self._record_collisions()
        for agent in collided_agents:
            rewards[agent] -= 0.1

        captures = self._capture_targets()
        for agent, count in captures.items():
            rewards[agent] += float(count)

        all_done = not any(target.active for target in self.targets)
        truncated = self.steps >= self.max_cycles
        terminations = {agent: all_done for agent in self.agents}
        truncations = {agent: truncated for agent in self.agents}
        observations = self._observations()
        infos = self._infos()

        if all_done or truncated:
            self.agents = []

        return observations, rewards, terminations, truncations, infos

    def state(self) -> np.ndarray:
        drone_state = np.concatenate(
            [
                self.drone_positions[agent] / (self.grid_size - 1)
                for agent in self.possible_agents
            ]
        )
        target_state = np.concatenate(
            [
                np.array(
                    [
                        target.position[0] / (self.grid_size - 1),
                        target.position[1] / (self.grid_size - 1),
                        float(target.active),
                    ],
                    dtype=np.float32,
                )
                for target in self.targets
            ]
        )
        return np.concatenate([drone_state, target_state]).astype(np.float32)

    def render(self) -> str:
        grid = np.full((self.grid_size, self.grid_size), ".", dtype=object)
        for x, y in self.no_fly_zones:
            grid[self.grid_size - 1 - y, x] = "X"
        for idx, target in enumerate(self.targets):
            if target.active:
                x, y = target.position
                grid[self.grid_size - 1 - y, x] = f"T{idx}"
        for idx, agent in enumerate(self.possible_agents):
            if agent in self.drone_positions:
                x, y = self.drone_positions[agent]
                grid[self.grid_size - 1 - y, x] = f"D{idx}"
        return "\n".join(" ".join(str(cell).rjust(2) for cell in row) for row in grid)

    def close(self) -> None:
        return None

    @property
    def completed_target_count(self) -> int:
        return self.num_targets - sum(target.active for target in self.targets)

    def snapshot(self) -> dict[str, Any]:
        return {
            "step": self.steps,
            "grid_size": self.grid_size,
            "drones": {
                agent: self.drone_positions[agent].astype(int).tolist()
                for agent in self.possible_agents
            },
            "targets": [
                {
                    "position": target.position.astype(int).tolist(),
                    "active": target.active,
                }
                for target in self.targets
            ],
            "no_fly_zones": [list(cell) for cell in sorted(self.no_fly_zones)],
            "safety_summary": self.safety_summary(),
        }

    def safety_summary(self) -> dict[str, Any]:
        no_fly_total = sum(self.no_fly_violations.values())
        return {
            "episode_step": self.steps,
            "collision_events": self.collision_events,
            "no_fly_violations": no_fly_total,
            "target_captures": sum(self.target_captures.values()),
            "total_violations": self.collision_events + no_fly_total,
            "by_agent": {
                agent: {
                    "no_fly_violations": self.no_fly_violations.get(agent, 0),
                    "target_captures": self.target_captures.get(agent, 0),
                }
                for agent in self.possible_agents
            },
        }

    def _sample_empty_cell(self, occupied: set[tuple[int, int]]) -> np.ndarray:
        while True:
            cell = self.np_random.integers(0, self.grid_size, size=2, dtype=np.int32)
            key = tuple(cell.tolist())
            if key not in occupied:
                occupied.add(key)
                return cell

    def _observations(self) -> dict[str, np.ndarray]:
        return {agent: self._observe(agent) for agent in self.agents}

    def _observe(self, agent: str) -> np.ndarray:
        position = self.drone_positions[agent].astype(np.float32)
        target = self._nearest_active_target(position)
        if target is None:
            target_position = position
            active = 0.0
        else:
            target_position = target.position.astype(np.float32)
            active = 1.0
        delta = target_position - position
        nearest_no_fly_distance = self._nearest_no_fly_distance(position)
        return np.array(
            [
                position[0] / (self.grid_size - 1),
                position[1] / (self.grid_size - 1),
                target_position[0] / (self.grid_size - 1),
                target_position[1] / (self.grid_size - 1),
                abs(delta[0]) / (self.grid_size - 1),
                abs(delta[1]) / (self.grid_size - 1),
                active,
                nearest_no_fly_distance / (2 * (self.grid_size - 1)),
            ],
            dtype=np.float32,
        )

    def _nearest_active_target(self, position: np.ndarray) -> Target | None:
        active_targets = [target for target in self.targets if target.active]
        if not active_targets:
            return None
        return min(active_targets, key=lambda target: np.linalg.norm(target.position - position, ord=1))

    def _nearest_no_fly_distance(self, position: np.ndarray) -> float:
        if not self.no_fly_zones:
            return float(2 * (self.grid_size - 1))
        return float(
            min(
                np.linalg.norm(np.array(cell, dtype=np.float32) - position, ord=1)
                for cell in self.no_fly_zones
            )
        )

    def _record_collisions(self) -> set[str]:
        positions: dict[tuple[int, int], list[str]] = {}
        for agent in self.agents:
            key = tuple(self.drone_positions[agent].tolist())
            positions.setdefault(key, []).append(agent)

        collided_agents: set[str] = set()
        for agents in positions.values():
            if len(agents) < 2:
                continue
            self.collision_events += 1
            collided_agents.update(agents)
        return collided_agents

    def _capture_targets(self) -> dict[str, int]:
        captures = {agent: 0 for agent in self.agents}
        for idx, target in enumerate(self.targets):
            if not target.active:
                continue
            for agent in self.agents:
                distance = np.linalg.norm(self.drone_positions[agent] - target.position, ord=1)
                if distance <= self.capture_radius:
                    self.targets[idx] = Target(position=target.position, active=False)
                    self.target_captures[agent] += 1
                    captures[agent] += 1
                    break
        return captures

    def _infos(self) -> dict[str, dict[str, Any]]:
        completed = self.completed_target_count
        return {
            agent: {
                "episode_step": self.steps,
                "completed_targets": completed,
                "completion_rate": completed / self.num_targets,
                "no_fly_violations": self.no_fly_violations.get(agent, 0),
                "target_captures": self.target_captures.get(agent, 0),
            }
            for agent in self.agents
        }


if __name__ == "__main__":
    env = DroneSearchEnv()
    observations, infos = env.reset(seed=7)
    print("Initial observations:", observations)
    print("Initial infos:", infos)
    print(env.render())
