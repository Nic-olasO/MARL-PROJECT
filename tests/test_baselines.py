import numpy as np

from marl_practice.baselines import GreedyNearestTaskPolicy, RandomPolicy, run_episode
from marl_practice.baselines.task_allocation import main
from marl_practice.envs.task_allocation_env import TaskAllocationEnv
from marl_practice.logging import read_episode_records


def test_greedy_policy_selects_deterministic_actions_from_observation():
    policy = GreedyNearestTaskPolicy()

    serve_obs = np.array([0.5, 0.5, 0.5, 0.5, 0.0, 1.0], dtype=np.float32)
    right_obs = np.array([0.2, 0.5, 0.8, 0.5, 0.3, 1.0], dtype=np.float32)
    left_obs = np.array([0.8, 0.5, 0.2, 0.5, 0.3, 1.0], dtype=np.float32)
    up_obs = np.array([0.5, 0.2, 0.5, 0.8, 0.3, 1.0], dtype=np.float32)
    down_obs = np.array([0.5, 0.8, 0.5, 0.2, 0.3, 1.0], dtype=np.float32)
    hidden_obs = np.array([0.5, 0.5, 0.0, 0.0, 0.0, 0.0], dtype=np.float32)

    assert policy("agent_0", serve_obs) == 5
    assert policy("agent_0", right_obs) == 4
    assert policy("agent_0", left_obs) == 3
    assert policy("agent_0", up_obs) == 1
    assert policy("agent_0", down_obs) == 2
    assert policy("agent_0", hidden_obs) == 0


def test_random_episode_runs_to_completion():
    env = TaskAllocationEnv(num_agents=2, num_tasks=2, grid_size=5, max_cycles=4)

    summary = run_episode(env, RandomPolicy(seed=123), seed=123)

    assert summary["steps"] <= 4
    assert set(summary["per_agent_returns"]) == {"agent_0", "agent_1"}
    assert summary["episode_return"] == sum(summary["per_agent_returns"].values())
    assert "completed_tasks" in summary
    assert "completion_rate" in summary
    assert "safety_summary" in summary
    assert "collision_events" in summary["safety_summary"]
    assert env.agents == []


def test_greedy_episode_runs_to_completion():
    env = TaskAllocationEnv(num_agents=2, num_tasks=2, grid_size=5, max_cycles=20)

    summary = run_episode(env, GreedyNearestTaskPolicy(), seed=7)

    assert 1 <= summary["steps"] <= 20
    assert set(summary["per_agent_returns"]) == {"agent_0", "agent_1"}
    assert summary["completed_tasks"] == 2
    assert summary["completion_rate"] == 1.0
    assert summary["safety_summary"]["invalid_serves"] >= 0
    assert env.agents == []


def test_baseline_cli_appends_episode_jsonl(tmp_path):
    log_path = tmp_path / "episodes.jsonl"

    summary = main(
        [
            "--policy",
            "greedy",
            "--seed",
            "7",
            "--num-agents",
            "2",
            "--num-tasks",
            "2",
            "--grid-size",
            "5",
            "--max-cycles",
            "20",
            "--log-path",
            str(log_path),
        ]
    )

    records = read_episode_records(log_path)
    assert len(records) == 1
    assert records[0]["seed"] == 7
    assert records[0]["policy_name"] == "greedy"
    assert records[0]["completed_tasks"] == summary["completed_tasks"]
    assert records[0]["safety_summary"] == summary["safety_summary"]
