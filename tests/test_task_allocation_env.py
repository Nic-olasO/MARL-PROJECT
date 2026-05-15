import json

import numpy as np
from pettingzoo.test import parallel_api_test

from marl_practice.envs.task_allocation_env import Task, TaskAllocationEnv


def test_parallel_api_contract():
    env = TaskAllocationEnv(max_cycles=5)
    parallel_api_test(env, num_cycles=10)


def test_reset_and_step_shapes():
    env = TaskAllocationEnv(num_agents=2, num_tasks=2, grid_size=5, max_cycles=3)
    observations, infos = env.reset(seed=42)

    assert set(observations) == {"agent_0", "agent_1"}
    assert set(infos) == {"agent_0", "agent_1"}
    assert observations["agent_0"].shape == (6,)
    assert observations["agent_0"].dtype == np.float32

    actions = {agent: env.action_space(agent).sample() for agent in env.agents}
    observations, rewards, terminations, truncations, infos = env.step(actions)

    assert set(observations) == {"agent_0", "agent_1"}
    assert set(rewards) == {"agent_0", "agent_1"}
    assert set(terminations) == {"agent_0", "agent_1"}
    assert set(truncations) == {"agent_0", "agent_1"}
    assert set(infos) == {"agent_0", "agent_1"}
    assert env.state().dtype == np.float32


def test_reward_modes_distribute_completion_reward():
    expected_rewards = {
        "individual": {"agent_0": 0.99, "agent_1": -0.01},
        "team": {"agent_0": 0.99, "agent_1": 0.99},
        "mixed": {"agent_0": 0.99, "agent_1": 0.49},
    }

    for reward_mode, expected in expected_rewards.items():
        env = TaskAllocationEnv(
            num_agents=2,
            num_tasks=1,
            grid_size=5,
            max_cycles=3,
            reward_mode=reward_mode,
        )
        env.reset(seed=7)
        env.agent_positions["agent_0"] = np.array([1, 1], dtype=np.int32)
        env.agent_positions["agent_1"] = np.array([4, 4], dtype=np.int32)
        env.tasks = [Task(position=np.array([1, 1], dtype=np.int32), active=True)]

        _, rewards, terminations, truncations, _ = env.step(
            {"agent_0": env.SERVE, "agent_1": 0}
        )

        assert rewards == expected
        assert terminations == {"agent_0": True, "agent_1": True}
        assert truncations == {"agent_0": False, "agent_1": False}


def test_reset_is_deterministic_for_same_seed():
    env_a = TaskAllocationEnv(num_agents=2, num_tasks=3, grid_size=6)
    env_b = TaskAllocationEnv(num_agents=2, num_tasks=3, grid_size=6)

    observations_a, infos_a = env_a.reset(seed=123)
    observations_b, infos_b = env_b.reset(seed=123)

    assert infos_a == infos_b
    assert np.array_equal(env_a.state(), env_b.state())
    for agent in env_a.possible_agents:
        assert np.array_equal(observations_a[agent], observations_b[agent])


def test_max_cycles_truncates_episode():
    env = TaskAllocationEnv(num_agents=2, num_tasks=1, grid_size=5, max_cycles=1)
    env.reset(seed=11)
    env.agent_positions["agent_0"] = np.array([0, 0], dtype=np.int32)
    env.agent_positions["agent_1"] = np.array([4, 4], dtype=np.int32)
    env.tasks = [Task(position=np.array([2, 2], dtype=np.int32), active=True)]

    _, _, terminations, truncations, infos = env.step({"agent_0": 0, "agent_1": 0})

    assert terminations == {"agent_0": False, "agent_1": False}
    assert truncations == {"agent_0": True, "agent_1": True}
    assert infos["agent_0"]["episode_step"] == 1
    assert env.agents == []


def test_view_radius_hides_distant_tasks_without_changing_shape():
    env = TaskAllocationEnv(num_agents=1, num_tasks=1, grid_size=5, view_radius=1)
    env.reset(seed=19)
    env.agent_positions["agent_0"] = np.array([0, 0], dtype=np.int32)
    env.tasks = [Task(position=np.array([4, 4], dtype=np.int32), active=True)]

    observations, _, _, _, _ = env.step({"agent_0": 0})

    observation = observations["agent_0"]
    assert observation.shape == (6,)
    assert np.array_equal(observation[:4], np.array([0.0, 0.0, 0.0, 0.0], dtype=np.float32))
    assert observation[5] == 0.0


def test_info_metrics_track_progress_and_invalid_serves():
    env = TaskAllocationEnv(num_agents=2, num_tasks=2, grid_size=5, max_cycles=5)
    _, infos = env.reset(seed=3)

    assert infos["agent_0"] == {
        "active_tasks": 2,
        "completed_tasks": 0,
        "completion_rate": 0.0,
        "episode_step": 0,
        "invalid_serves": 0,
    }

    env.agent_positions["agent_0"] = np.array([0, 0], dtype=np.int32)
    env.agent_positions["agent_1"] = np.array([4, 4], dtype=np.int32)
    env.tasks = [
        Task(position=np.array([1, 1], dtype=np.int32), active=True),
        Task(position=np.array([2, 2], dtype=np.int32), active=True),
    ]

    env.step({"agent_0": env.SERVE, "agent_1": 0})
    env.agent_positions["agent_0"] = np.array([1, 1], dtype=np.int32)
    _, _, _, _, infos = env.step({"agent_0": env.SERVE, "agent_1": 0})

    assert infos["agent_0"] == {
        "active_tasks": 1,
        "completed_tasks": 1,
        "completion_rate": 0.5,
        "episode_step": 2,
        "invalid_serves": 1,
    }
    assert infos["agent_1"]["invalid_serves"] == 0


def test_safety_summary_tracks_invalid_serves_and_collisions():
    env = TaskAllocationEnv(num_agents=2, num_tasks=1, grid_size=5, max_cycles=5)
    env.reset(seed=23)
    env.agent_positions["agent_0"] = np.array([1, 1], dtype=np.int32)
    env.agent_positions["agent_1"] = np.array([1, 1], dtype=np.int32)
    env.tasks = [Task(position=np.array([4, 4], dtype=np.int32), active=True)]

    env.step({"agent_0": env.SERVE, "agent_1": 0})

    assert env.safety_summary() == {
        "episode_step": 1,
        "invalid_serves": 1,
        "collision_events": 1,
        "collision_involvements": 2,
        "total_violations": 2,
        "by_agent": {
            "agent_0": {
                "invalid_serves": 1,
                "collisions": 1,
                "total": 2,
            },
            "agent_1": {
                "invalid_serves": 0,
                "collisions": 1,
                "total": 1,
            },
        },
    }
    json.dumps(env.safety_summary())


def test_safety_summary_resets_each_episode():
    env = TaskAllocationEnv(num_agents=2, num_tasks=1, grid_size=5)
    env.reset(seed=29)
    env.agent_positions["agent_0"] = np.array([2, 2], dtype=np.int32)
    env.agent_positions["agent_1"] = np.array([2, 2], dtype=np.int32)
    env.tasks = [Task(position=np.array([0, 0], dtype=np.int32), active=True)]

    env.step({"agent_0": env.SERVE, "agent_1": 0})
    env.reset(seed=31)

    assert env.safety_summary() == {
        "episode_step": 0,
        "invalid_serves": 0,
        "collision_events": 0,
        "collision_involvements": 0,
        "total_violations": 0,
        "by_agent": {
            "agent_0": {
                "invalid_serves": 0,
                "collisions": 0,
                "total": 0,
            },
            "agent_1": {
                "invalid_serves": 0,
                "collisions": 0,
                "total": 0,
            },
        },
    }
