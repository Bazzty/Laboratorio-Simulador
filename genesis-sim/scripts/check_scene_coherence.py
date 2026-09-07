"""Coherence smoke test for a lab10 scene: physics-settle check.

Run via `simctl run <scene> scripts/check_scene_coherence.py` with the
SCENE_NAME env var set to the scenario's basename (e.g. "scene_1"). Compares
each box object's settled pose against the pose declared in the scenario YAML
and exits non-zero if any cube drifted, fell through the table, or failed to
land on its stack target.
"""

import os
import sys
import time

import requests
import yaml

TOL_XY = 0.03  # metres
TOL_Z = 0.035
SETTLE_SECONDS = 3.0
POLL_INTERVAL = 0.3


def load_expected(scene_name):
    path = os.path.join(os.path.dirname(__file__), "..", "configs", "scenarios", f"{scene_name}.yml")
    with open(path) as f:
        config = yaml.safe_load(f)

    expected = {}
    for obj in config.get("objects", []):
        if obj.get("type") == "box":
            expected[obj["name"]] = obj["pos"]
    return expected


def main():
    scene_name = os.environ["SCENE_NAME"]
    base_url = os.environ["MANITO_URL"].rstrip("/")
    expected = load_expected(scene_name)

    time.sleep(SETTLE_SECONDS)
    resp = requests.get(f"{base_url}/api/v1/state", timeout=10)
    resp.raise_for_status()
    entities = resp.json().get("entities") or {}

    ok = True
    print(f"--- {scene_name}: {len(expected)} cubos esperados ---")
    for name, exp_pos in expected.items():
        actual = entities.get(name)
        if actual is None:
            print(f"[FALTA] {name}: no aparece en /api/v1/state")
            ok = False
            continue

        dx, dy, dz = (a - e for a, e in zip(actual, exp_pos))
        xy_off = (dx**2 + dy**2) ** 0.5
        z_off = abs(dz)
        status = "OK" if xy_off <= TOL_XY and z_off <= TOL_Z else "DESVIADO"
        if status != "OK":
            ok = False
        print(
            f"[{status}] {name}: esperado={exp_pos} actual={[round(v, 3) for v in actual]} "
            f"dxy={xy_off:.3f} dz={z_off:.3f}"
        )

    print("RESULTADO:", "COHERENTE" if ok else "INCOHERENTE")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
