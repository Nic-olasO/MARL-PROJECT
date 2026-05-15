from __future__ import annotations

from marl_practice.dashboard.server import dashboard_payload, summarize_records
from marl_practice.logging import append_jsonl


def test_summarize_records_handles_empty_data():
    assert summarize_records([]) == {
        "episodes": 0,
        "avg_return": 0.0,
        "avg_completion_rate": 0.0,
        "total_completed_tasks": 0,
        "total_safety_violations": 0,
        "policies": [],
    }


def test_summarize_records_aggregates_episode_metrics():
    summary = summarize_records(
        [
            {
                "policy_name": "greedy",
                "episode_return": 2.0,
                "completion_rate": 1.0,
                "completed_tasks": 2,
                "safety_summary": {"total_violations": 3},
            },
            {
                "policy_name": "random",
                "episode_return": -1.0,
                "completion_rate": 0.5,
                "completed_tasks": 1,
                "safety_summary": {"invalid_serves": 2, "collision_events": 1},
            },
        ]
    )

    assert summary == {
        "episodes": 2,
        "avg_return": 0.5,
        "avg_completion_rate": 0.75,
        "total_completed_tasks": 3,
        "total_safety_violations": 6,
        "policies": ["greedy", "random"],
    }


def test_dashboard_payload_reads_jsonl(tmp_path):
    log_path = tmp_path / "episodes.jsonl"
    append_jsonl(
        log_path,
        {
            "seed": 7,
            "policy_name": "greedy",
            "episode_return": 1.5,
            "steps": 4,
            "completed_tasks": 2,
            "completion_rate": 1.0,
            "safety_summary": {"total_violations": 0},
        },
    )

    payload = dashboard_payload(log_path)

    assert payload["log_path"] == str(log_path)
    assert payload["summary"]["episodes"] == 1
    assert payload["episodes"][0]["seed"] == 7
