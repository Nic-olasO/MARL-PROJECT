from __future__ import annotations

from pathlib import Path

import pytest


CONFIG_PATH = Path(__file__).resolve().parents[1] / "configs" / "ippo_task_allocation.yaml"


def test_ippo_config_file_exists():
    assert CONFIG_PATH.exists()


def test_ippo_config_composes_with_hydra():
    pytest.importorskip("hydra")
    from hydra import compose, initialize_config_dir

    with initialize_config_dir(config_dir=str(CONFIG_PATH.parent), version_base="1.3"):
        cfg = compose(config_name=CONFIG_PATH.stem)

    assert cfg.experiment.name == "ippo_task_allocation"
    assert cfg.env.name == "marl_practice_task_allocation_v0"
    assert cfg.env.config.num_agents == 3
    assert cfg.algorithm.name == "IPPO"
    assert cfg.algorithm.num_rollout_workers == 0

