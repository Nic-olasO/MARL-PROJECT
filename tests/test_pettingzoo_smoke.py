from __future__ import annotations

from marl_sim.smoke_pettingzoo import run_random_episode


def test_pettingzoo_classic_smoke_runs(capsys):
    run_random_episode(seed=7, max_cycles=20)

    captured = capsys.readouterr()
    assert "PettingZoo smoke simulation complete." in captured.out
    assert "player_1" in captured.out
    assert "player_2" in captured.out
