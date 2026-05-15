from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from marl_practice.envs.task_allocation_env import TaskAllocationEnv


DEFAULT_RLLIB_ENV_NAME = "marl_practice_task_allocation_v0"

DEFAULT_TASK_ALLOCATION_ENV_CONFIG: dict[str, Any] = {
    "num_agents": 3,
    "num_tasks": 4,
    "grid_size": 8,
    "max_cycles": 50,
}


class RLLibUnavailableError(ImportError):
    """Raised when optional RLlib adapters are requested without Ray installed."""


@dataclass(frozen=True)
class RLLibEnvRegistration:
    """Description of a registered RLlib environment."""

    name: str = DEFAULT_RLLIB_ENV_NAME
    creator: str = "marl_practice.training.rllib_env:rllib_env_creator"


def _clean_env_config(env_config: Mapping[str, Any] | None = None) -> dict[str, Any]:
    config = dict(DEFAULT_TASK_ALLOCATION_ENV_CONFIG)
    if env_config:
        config.update(dict(env_config))
    return config


def task_allocation_parallel_env_creator(
    env_config: Mapping[str, Any] | None = None,
) -> TaskAllocationEnv:
    """Create the underlying PettingZoo parallel task-allocation environment."""

    return TaskAllocationEnv(**_clean_env_config(env_config))


def rllib_env_creator(env_config: Mapping[str, Any] | None = None):
    """Create an RLlib-compatible wrapper around the PettingZoo environment."""

    try:
        from ray.rllib.env.wrappers.pettingzoo_env import ParallelPettingZooEnv
    except ImportError as exc:
        raise RLLibUnavailableError(
            "RLlib is required to create the wrapped task-allocation env. "
            "Install the training extras from requirements-marl.txt."
        ) from exc

    return ParallelPettingZooEnv(task_allocation_parallel_env_creator(env_config))


def register_task_allocation_env(
    env_name: str = DEFAULT_RLLIB_ENV_NAME,
) -> RLLibEnvRegistration:
    """Register the task-allocation env with RLlib and return registration metadata."""

    try:
        from ray.tune.registry import register_env
    except ImportError as exc:
        raise RLLibUnavailableError(
            "Ray Tune is required to register the task-allocation env with RLlib."
        ) from exc

    register_env(env_name, rllib_env_creator)
    return RLLibEnvRegistration(name=env_name)
