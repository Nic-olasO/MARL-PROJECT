from __future__ import annotations

import argparse
import json
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any, Protocol

import numpy as np

from marl_practice.envs.task_allocation_env import TaskAllocationEnv
from marl_practice.logging import EpisodeRecord, write_episode_record


PolicyFn = Callable[[str, np.ndarray, Any], int]


class Policy(Protocol):
    def __call__(self, agent: str, observation: np.ndarray, env: Any) -> int:
        """Return an action for one agent."""


class RandomPolicy:
    """Uniform random policy over each agent's action space."""

    def __init__(self, seed: int | None = None) -> None:
        self.rng = np.random.default_rng(seed)

    def __call__(self, agent: str, observation: np.ndarray, env: Any) -> int:
        del observation
        return int(self.rng.integers(env.action_space(agent).n))


class GreedyNearestTaskPolicy:
    """Move toward the nearest visible task from the observation vector."""

    NO_OP = 0
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4
    SERVE = 5

    def __init__(self, tolerance: float = 1e-6) -> None:
        self.tolerance = tolerance

    def __call__(self, agent: str, observation: np.ndarray, env: Any = None) -> int:
        del agent, env
        agent_x, agent_y, task_x, task_y, distance, active = observation
        if active < 0.5:
            return self.NO_OP
        if distance <= self.tolerance:
            return self.SERVE
        if task_x > agent_x + self.tolerance:
            return self.RIGHT
        if task_x < agent_x - self.tolerance:
            return self.LEFT
        if task_y > agent_y + self.tolerance:
            return self.UP
        if task_y < agent_y - self.tolerance:
            return self.DOWN
        return self.SERVE


def run_episode(
    env: Any,
    policy: Policy | PolicyFn | Mapping[str, Policy | PolicyFn],
    seed: int | None = None,
    policy_name: str | None = None,
) -> dict[str, Any]:
    """Run one parallel-env episode and return a plain summary dict."""

    observations, infos = env.reset(seed=seed)
    per_agent_returns = {agent: 0.0 for agent in env.possible_agents}
    steps = 0
    last_infos = infos

    while getattr(env, "agents", []):
        actions = {
            agent: _select_action(policy, agent, observations[agent], env)
            for agent in env.agents
        }
        observations, rewards, terminations, truncations, infos = env.step(actions)
        del terminations, truncations
        steps += 1
        last_infos = infos

        for agent, reward in rewards.items():
            per_agent_returns[agent] = per_agent_returns.get(agent, 0.0) + float(reward)

    summary: dict[str, Any] = {
        "seed": seed,
        "policy_name": policy_name or _policy_name(policy),
        "steps": steps,
        "per_agent_returns": per_agent_returns,
        "episode_return": float(sum(per_agent_returns.values())),
    }
    summary.update(_episode_metrics(last_infos, env))
    return summary


def _select_action(
    policy: Policy | PolicyFn | Mapping[str, Policy | PolicyFn],
    agent: str,
    observation: np.ndarray,
    env: Any,
) -> int:
    if isinstance(policy, Mapping):
        agent_policy = policy[agent]
    else:
        agent_policy = policy
    return int(agent_policy(agent, observation, env))


def _episode_metrics(infos: Mapping[str, Mapping[str, Any]], env: Any) -> dict[str, Any]:
    if not infos:
        metrics: dict[str, Any] = {}
    else:
        first_info = next(iter(infos.values()))
        metrics = {}
        for key in ("completed_tasks", "completion_rate"):
            if key in first_info:
                metrics[key] = first_info[key]

    if hasattr(env, "completed_task_count"):
        metrics.setdefault("completed_tasks", int(env.completed_task_count))
    if hasattr(env, "num_tasks") and env.num_tasks:
        metrics.setdefault("completion_rate", int(env.completed_task_count) / env.num_tasks)

    if hasattr(env, "safety_summary"):
        metrics["safety_summary"] = env.safety_summary()
    elif any("invalid_serves" in info for info in infos.values()):
        metrics["safety_summary"] = {
            "invalid_serves": {
                agent: int(info.get("invalid_serves", 0))
                for agent, info in infos.items()
            },
            "total_invalid_serves": int(
                sum(info.get("invalid_serves", 0) for info in infos.values())
            ),
        }
    return metrics


def _policy_name(policy: Policy | PolicyFn | Mapping[str, Policy | PolicyFn]) -> str:
    if isinstance(policy, Mapping):
        return "mapped_policy"
    policy_type = type(policy)
    if policy_type is not type(lambda: None):
        return policy_type.__name__
    return getattr(policy, "__name__", "policy")


def _episode_record(summary: Mapping[str, Any]) -> EpisodeRecord:
    return EpisodeRecord(
        seed=summary.get("seed"),
        policy_name=str(summary["policy_name"]),
        episode_return=float(summary["episode_return"]),
        steps=int(summary["steps"]),
        completed_tasks=int(summary.get("completed_tasks", 0)),
        completion_rate=float(summary.get("completion_rate", 0.0)),
        safety_summary=summary.get("safety_summary"),
        per_agent_returns=summary.get("per_agent_returns"),
    )


def main(argv: list[str] | None = None) -> dict[str, Any]:
    parser = argparse.ArgumentParser(description="Run TaskAllocationEnv baselines.")
    parser.add_argument("--policy", choices=("random", "greedy"), default="greedy")
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--num-agents", type=int, default=3)
    parser.add_argument("--num-tasks", type=int, default=4)
    parser.add_argument("--grid-size", type=int, default=8)
    parser.add_argument("--max-cycles", type=int, default=50)
    parser.add_argument(
        "--log-path",
        type=Path,
        default=None,
        help="Optional JSONL path where the episode record should be appended.",
    )
    args = parser.parse_args(argv)

    env = TaskAllocationEnv(
        num_agents=args.num_agents,
        num_tasks=args.num_tasks,
        grid_size=args.grid_size,
        max_cycles=args.max_cycles,
    )
    policy = (
        RandomPolicy(seed=args.seed)
        if args.policy == "random"
        else GreedyNearestTaskPolicy()
    )
    summary = run_episode(env, policy, seed=args.seed, policy_name=args.policy)
    if args.log_path is not None:
        write_episode_record(args.log_path, _episode_record(summary))
    print(json.dumps(summary, sort_keys=True))
    return summary


if __name__ == "__main__":
    main()
