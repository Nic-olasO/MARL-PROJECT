from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw

from marl_practice.envs.drone_search_env import DroneSearchEnv
from marl_practice.logging import write_episode_record


class GreedyDronePolicy:
    """Scripted policy that moves each drone toward its nearest active target."""

    NO_OP = 0
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4

    def __call__(self, observation) -> int:
        drone_x, drone_y, target_x, target_y, delta_x, delta_y, active, _ = observation
        if active < 0.5:
            return self.NO_OP
        if delta_x == 0 and delta_y == 0:
            return self.NO_OP
        if abs(target_x - drone_x) >= abs(target_y - drone_y):
            return self.RIGHT if target_x > drone_x else self.LEFT
        return self.UP if target_y > drone_y else self.DOWN


def run_drone_demo(
    seed: int = 7,
    num_drones: int = 3,
    num_targets: int = 5,
    grid_size: int = 12,
    max_cycles: int = 80,
    num_no_fly_zones: int = 6,
) -> dict[str, Any]:
    env = DroneSearchEnv(
        num_drones=num_drones,
        num_targets=num_targets,
        grid_size=grid_size,
        max_cycles=max_cycles,
        num_no_fly_zones=num_no_fly_zones,
    )
    policy = GreedyDronePolicy()
    observations, _ = env.reset(seed=seed)
    frames = [env.snapshot()]
    per_agent_returns = {agent: 0.0 for agent in env.possible_agents}

    while env.agents:
        actions = {agent: policy(observations[agent]) for agent in env.agents}
        observations, rewards, _, _, _ = env.step(actions)
        for agent, reward in rewards.items():
            per_agent_returns[agent] += float(reward)
        frames.append(env.snapshot())

    return {
        "seed": seed,
        "policy_name": "greedy_drone",
        "steps": env.steps,
        "episode_return": float(sum(per_agent_returns.values())),
        "per_agent_returns": per_agent_returns,
        "completed_targets": env.completed_target_count,
        "completion_rate": env.completed_target_count / env.num_targets,
        "safety_summary": env.safety_summary(),
        "frames": frames,
    }


def render_trace_to_gif(
    trace: dict[str, Any],
    output_path: str | Path,
    cell_size: int = 48,
    frame_duration_ms: int = 180,
) -> Path:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    images = [_render_frame(frame, cell_size) for frame in trace["frames"]]
    images[0].save(
        output,
        save_all=True,
        append_images=images[1:],
        duration=frame_duration_ms,
        loop=0,
    )
    return output


def drone_episode_record(
    trace: dict[str, Any],
    video_path: str | Path,
    trace_path: str | Path,
) -> dict[str, Any]:
    """Build the shared JSONL episode record for a drone demo run."""

    return {
        "seed": trace["seed"],
        "policy_name": trace["policy_name"],
        "episode_return": trace["episode_return"],
        "steps": trace["steps"],
        "completed_tasks": trace["completed_targets"],
        "completed_targets": trace["completed_targets"],
        "completion_rate": trace["completion_rate"],
        "safety_summary": trace["safety_summary"],
        "per_agent_returns": trace["per_agent_returns"],
        "artifact_paths": {
            "video": str(video_path),
            "trace": str(trace_path),
        },
        "environment": "drone_search_v0",
    }


def _render_frame(frame: dict[str, Any], cell_size: int) -> Image.Image:
    grid_size = int(frame["grid_size"])
    margin = 36
    width = grid_size * cell_size
    height = grid_size * cell_size + margin
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)

    for index in range(grid_size + 1):
        x = index * cell_size
        y = margin + index * cell_size
        draw.line((x, margin, x, height), fill=(220, 220, 220))
        draw.line((0, y, width, y), fill=(220, 220, 220))

    for x, y in frame["no_fly_zones"]:
        _draw_cell(draw, x, y, grid_size, cell_size, margin, fill=(234, 84, 85), label="X")

    for idx, target in enumerate(frame["targets"]):
        if not target["active"]:
            continue
        x, y = target["position"]
        _draw_cell(draw, x, y, grid_size, cell_size, margin, fill=(69, 179, 107), label=f"T{idx}")

    drone_colors = [(46, 134, 193), (155, 89, 182), (243, 156, 18), (44, 62, 80)]
    for idx, (agent, position) in enumerate(sorted(frame["drones"].items())):
        x, y = position
        left, top, right, bottom = _cell_bounds(x, y, grid_size, cell_size, margin)
        inset = max(5, cell_size // 7)
        color = drone_colors[idx % len(drone_colors)]
        draw.ellipse((left + inset, top + inset, right - inset, bottom - inset), fill=color)
        draw.text((left + inset + 2, top + inset + 2), agent.replace("drone_", "D"), fill="white")

    safety = frame["safety_summary"]
    title = (
        f"step {frame['step']} | captures {safety['target_captures']} | "
        f"violations {safety['total_violations']}"
    )
    draw.text((8, 10), title, fill=(20, 20, 20))
    return image


def _draw_cell(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    grid_size: int,
    cell_size: int,
    margin: int,
    fill: tuple[int, int, int],
    label: str,
) -> None:
    left, top, right, bottom = _cell_bounds(x, y, grid_size, cell_size, margin)
    draw.rectangle((left + 3, top + 3, right - 3, bottom - 3), fill=fill)
    draw.text((left + 8, top + 8), label, fill="white")


def _cell_bounds(
    x: int,
    y: int,
    grid_size: int,
    cell_size: int,
    margin: int,
) -> tuple[int, int, int, int]:
    left = x * cell_size
    top = margin + (grid_size - 1 - y) * cell_size
    return left, top, left + cell_size, top + cell_size


def main(argv: list[str] | None = None) -> dict[str, Any]:
    parser = argparse.ArgumentParser(description="Render a simple MARL drone demo GIF.")
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--num-drones", type=int, default=3)
    parser.add_argument("--num-targets", type=int, default=5)
    parser.add_argument("--grid-size", type=int, default=12)
    parser.add_argument("--max-cycles", type=int, default=80)
    parser.add_argument("--num-no-fly-zones", type=int, default=6)
    parser.add_argument("--output", type=Path, default=Path("runs/drone_demo.gif"))
    parser.add_argument("--trace-output", type=Path, default=Path("runs/drone_demo_trace.json"))
    parser.add_argument(
        "--log-path",
        type=Path,
        default=None,
        help="Optional JSONL path where the drone episode summary should be appended.",
    )
    args = parser.parse_args(argv)

    trace = run_drone_demo(
        seed=args.seed,
        num_drones=args.num_drones,
        num_targets=args.num_targets,
        grid_size=args.grid_size,
        max_cycles=args.max_cycles,
        num_no_fly_zones=args.num_no_fly_zones,
    )
    render_trace_to_gif(trace, args.output)
    args.trace_output.parent.mkdir(parents=True, exist_ok=True)
    args.trace_output.write_text(json.dumps(trace, indent=2, sort_keys=True), encoding="utf-8")
    if args.log_path is not None:
        write_episode_record(
            args.log_path,
            drone_episode_record(trace, args.output, args.trace_output),
        )
    print(json.dumps({key: trace[key] for key in trace if key != "frames"}, sort_keys=True))
    print(f"Wrote {args.output}")
    print(f"Wrote {args.trace_output}")
    if args.log_path is not None:
        print(f"Appended {args.log_path}")
    return trace


if __name__ == "__main__":
    main()
