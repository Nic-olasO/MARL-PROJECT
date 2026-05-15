from marl_practice.logging import read_episode_records
from marl_practice.visualization.drone_video import (
    drone_episode_record,
    main,
    render_trace_to_gif,
    run_drone_demo,
)


def test_drone_demo_generates_trace_and_gif(tmp_path):
    trace = run_drone_demo(
        seed=7,
        num_drones=2,
        num_targets=2,
        grid_size=6,
        max_cycles=20,
        num_no_fly_zones=2,
    )

    assert trace["steps"] <= 20
    assert trace["frames"]
    assert trace["frames"][0]["grid_size"] == 6
    assert "safety_summary" in trace

    output = render_trace_to_gif(trace, tmp_path / "drone_demo.gif", cell_size=24)
    assert output.exists()
    assert output.stat().st_size > 0


def test_drone_episode_record_uses_shared_logging_shape(tmp_path):
    trace = run_drone_demo(
        seed=7,
        num_drones=2,
        num_targets=2,
        grid_size=6,
        max_cycles=20,
        num_no_fly_zones=2,
    )

    record = drone_episode_record(
        trace,
        tmp_path / "drone_demo.gif",
        tmp_path / "drone_demo_trace.json",
    )

    assert record["seed"] == 7
    assert record["policy_name"] == "greedy_drone"
    assert record["completed_tasks"] == record["completed_targets"]
    assert record["environment"] == "drone_search_v0"
    assert record["artifact_paths"] == {
        "video": str(tmp_path / "drone_demo.gif"),
        "trace": str(tmp_path / "drone_demo_trace.json"),
    }
    assert "safety_summary" in record
    assert "per_agent_returns" in record


def test_drone_cli_appends_episode_jsonl(tmp_path):
    video_path = tmp_path / "drone_demo.gif"
    trace_path = tmp_path / "drone_demo_trace.json"
    log_path = tmp_path / "drone_episodes.jsonl"

    main(
        [
            "--seed",
            "7",
            "--num-drones",
            "2",
            "--num-targets",
            "2",
            "--grid-size",
            "6",
            "--max-cycles",
            "20",
            "--num-no-fly-zones",
            "2",
            "--output",
            str(video_path),
            "--trace-output",
            str(trace_path),
            "--log-path",
            str(log_path),
        ]
    )

    records = read_episode_records(log_path)
    assert len(records) == 1
    assert records[0]["seed"] == 7
    assert records[0]["policy_name"] == "greedy_drone"
    assert records[0]["environment"] == "drone_search_v0"
    assert records[0]["artifact_paths"] == {
        "trace": str(trace_path),
        "video": str(video_path),
    }
    assert video_path.exists()
    assert trace_path.exists()
