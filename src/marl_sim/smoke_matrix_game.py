from __future__ import annotations

from collections import Counter

from marl_sim.matrix_game import CoordinationGame


def run_random_episode(seed: int = 7) -> None:
    env = CoordinationGame(seed=seed)
    env.reset(seed=seed)

    total_rewards: Counter[str] = Counter()
    events: Counter[str] = Counter()

    terminated = False
    while not terminated:
        actions = {agent: env.sample_action() for agent in env.agents}
        result = env.step(actions)
        total_rewards.update(result.rewards)
        events[result.info["event"]] += 1
        terminated = result.terminated

    print("Matrix-game MARL smoke simulation complete.")
    print(f"Agents: {', '.join(env.agents)}")
    print(f"Total rewards: {dict(total_rewards)}")
    print(f"Events: {dict(events)}")


if __name__ == "__main__":
    run_random_episode()
