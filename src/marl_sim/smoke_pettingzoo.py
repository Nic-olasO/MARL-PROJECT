from __future__ import annotations

from collections import Counter

from pettingzoo.classic import tictactoe_v3


def run_random_episode(seed: int = 7, max_cycles: int = 100) -> None:
    """Run a tiny multi-agent smoke test using PettingZoo's AEC API."""
    env = tictactoe_v3.env(render_mode=None)
    env.reset(seed=seed)

    action_counts: Counter[str] = Counter()
    total_rewards: Counter[str] = Counter()

    for agent in env.agent_iter(max_iter=max_cycles):
        observation, reward, termination, truncation, _ = env.last()
        total_rewards[agent] += reward

        if termination or truncation:
            action = None
        else:
            action_mask = observation["action_mask"]
            legal_actions = [i for i, allowed in enumerate(action_mask) if allowed]
            action = legal_actions[0]
            action_counts[agent] += 1

        env.step(action)

    env.close()

    print("PettingZoo smoke simulation complete.")
    print(f"Agents: {', '.join(action_counts.keys())}")
    print(f"Actions taken: {dict(action_counts)}")
    print(f"Total rewards: {dict(total_rewards)}")


if __name__ == "__main__":
    run_random_episode()
