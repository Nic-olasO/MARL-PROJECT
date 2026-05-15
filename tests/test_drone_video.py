from marl_practice.visualization.drone_video import render_trace_to_gif, run_drone_demo


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
