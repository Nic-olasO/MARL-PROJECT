from __future__ import annotations

import pytest

from marl_practice.training.rllib_env import (
    DEFAULT_RLLIB_ENV_NAME,
    RLLibUnavailableError,
    rllib_env_creator,
    task_allocation_parallel_env_creator,
)


def test_task_allocation_parallel_env_creator_is_lightweight():
    env = task_allocation_parallel_env_creator(
        {
            "num_agents": 2,
            "num_tasks": 2,
            "grid_size": 5,
            "max_cycles": 3,
        }
    )

    observations, infos = env.reset(seed=123)

    assert env.metadata["name"] == "task_allocation_v0"
    assert env.possible_agents == ["agent_0", "agent_1"]
    assert set(observations) == {"agent_0", "agent_1"}
    assert set(infos) == {"agent_0", "agent_1"}

    env.close()


def test_rllib_env_creator_is_guarded_or_instantiates_wrapper():
    try:
        env = rllib_env_creator({"num_agents": 1, "num_tasks": 1, "max_cycles": 2})
    except RLLibUnavailableError:
        pytest.skip("RLlib is not installed in this test environment")

    observations, infos = env.reset(seed=123)
    assert observations
    assert infos is not None
    env.close()


def test_default_rllib_env_name_is_stable():
    assert DEFAULT_RLLIB_ENV_NAME == "marl_practice_task_allocation_v0"
