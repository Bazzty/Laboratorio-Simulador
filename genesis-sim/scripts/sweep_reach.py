"""Try a handful of simple move_joints() values and print where the gripper
actually lands, the same way pick_cube.py does. No inverse kinematics: just
sweep the shoulder angle (j1) at a couple of fixed (j3, z) poses so we can
place cubes wherever the arm naturally reaches, instead of the other way
around.
"""

import os

from manito_api import ManitoArm

BASE_URL = os.environ.get("MANITO_URL", "http://127.0.0.1:8000")


def end_effector(arm_state):
    import requests

    resp = requests.get(f"{BASE_URL}/api/v1/state", timeout=10)
    resp.raise_for_status()
    ee = resp.json().get("robot_end_effectors") or {}
    return next(iter(ee.values()))


def main():
    arm = ManitoArm(BASE_URL)
    arm.home()

    for j3, z in [(30, -10), (60, -10)]:
        print(f"--- j3={j3} z={z} ---")
        for j1 in [-60, -30, 0, 30, 60, 90]:
            arm.move_joints(j1, j3, 0, z)
            pos = end_effector(None)
            print(f"j1={j1:4} -> {[round(v, 3) for v in pos]}")


if __name__ == "__main__":
    main()
