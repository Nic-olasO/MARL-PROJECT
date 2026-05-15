from __future__ import annotations

import numpy as np

from marl_practice.logging import (
    EpisodeRecord,
    append_jsonl,
    read_episode_records,
    write_episode_record,
)


def test_episode_record_jsonl_round_trip(tmp_path):
    path = tmp_path / "episodes.jsonl"
    record = EpisodeRecord(
        seed=123,
        policy_name="random_baseline",
        episode_return=4.5,
        steps=10,
        completed_tasks=3,
        completion_rate=0.75,
        safety_summary={"invalid_serves": 1, "served_inactive_task": False},
        per_agent_returns={"agent_0": 2.0, "agent_1": 2.5},
    )

    write_episode_record(path, record)

    assert read_episode_records(path) == [
        {
            "seed": 123,
            "policy_name": "random_baseline",
            "episode_return": 4.5,
            "steps": 10,
            "completed_tasks": 3,
            "completion_rate": 0.75,
            "safety_summary": {"invalid_serves": 1, "served_inactive_task": False},
            "per_agent_returns": {"agent_0": 2.0, "agent_1": 2.5},
        }
    ]


def test_append_jsonl_accepts_dicts_and_multiple_records(tmp_path):
    path = tmp_path / "nested" / "episodes.jsonl"

    append_jsonl(path, {"seed": 1, "policy_name": "greedy"})
    append_jsonl(path, {"seed": 2, "policy_name": "random"})

    assert read_episode_records(path) == [
        {"seed": 1, "policy_name": "greedy"},
        {"seed": 2, "policy_name": "random"},
    ]


def test_episode_logging_converts_numpy_values(tmp_path):
    path = tmp_path / "episodes.jsonl"
    record = EpisodeRecord(
        seed=np.int64(7),
        policy_name="numpy_policy",
        episode_return=np.float32(1.25),
        steps=np.int32(5),
        completed_tasks=np.int64(2),
        completion_rate=np.float64(0.5),
        safety_summary={
            "invalid_serves": np.int64(0),
            "recent_rates": np.array([0.0, 0.5], dtype=np.float32),
        },
        per_agent_returns={"agent_0": np.float32(1.0), "agent_1": np.float64(0.25)},
    )

    write_episode_record(path, record)

    assert read_episode_records(path) == [
        {
            "seed": 7,
            "policy_name": "numpy_policy",
            "episode_return": 1.25,
            "steps": 5,
            "completed_tasks": 2,
            "completion_rate": 0.5,
            "safety_summary": {"invalid_serves": 0, "recent_rates": [0.0, 0.5]},
            "per_agent_returns": {"agent_0": 1.0, "agent_1": 0.25},
        }
    ]
