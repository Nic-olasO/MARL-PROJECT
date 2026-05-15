import numpy as np
from pettingzoo.test import parallel_api_test

from marl_practice.envs.drone_search_env import DroneSearchEnv, Target


def test_drone_env_parallel_api_contract():
    env = DroneSearchEnv(num_drones=2, num_targets=2, grid_size=6, max_cycles=5)
    parallel_api_test(env, num_cycles=10)


def test_drone_env_tracks_target_capture_and_safety():
    env = DroneSearchEnv(num_drones=2, num_targets=1, grid_size=5, max_cycles=3)
    observations, infos = env.reset(seed=7)
    assert set(observations) == {"drone_0", "drone_1"}
    assert infos["drone_0"]["completed_targets"] == 0

    env.drone_positions["drone_0"] = np.array([1, 1], dtype=np.int32)
    env.drone_positions["drone_1"] = np.array([1, 1], dtype=np.int32)
    env.targets = [Target(position=np.array([1, 1], dtype=np.int32), active=True)]
    env.no_fly_zones = {(1, 1)}

    _, rewards, terminations, _, infos = env.step({"drone_0": 0, "drone_1": 0})

    assert rewards["drone_0"] > 0
    assert terminations == {"drone_0": True, "drone_1": True}
    assert infos["drone_0"]["completed_targets"] == 1
    assert env.safety_summary()["collision_events"] == 1
    assert env.safety_summary()["no_fly_violations"] == 2


def test_drone_snapshot_is_json_ready():
    env = DroneSearchEnv(num_drones=1, num_targets=1, grid_size=5)
    env.reset(seed=11)
    snapshot = env.snapshot()

    assert snapshot["step"] == 0
    assert snapshot["grid_size"] == 5
    assert list(snapshot["drones"]) == ["drone_0"]
    assert snapshot["targets"][0]["active"] is True
