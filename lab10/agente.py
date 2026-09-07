"""Traduce un plan de pyperplan a movimientos reales del brazo Manito.

Uso:
    uv run python agente.py domain.pddl problems/problem_N.pddl [url]

`url` es la direccion del simulador/driver (por defecto MANITO_URL o
http://localhost:8080, ver manito_api.ManitoArm).

Las zonas se mueven variando solo el angulo de hombro (j1); j3 y las
profundidades de bajada quedan fijas, calibradas a mano probando
move_joints simples contra el simulador (ver CONTEXTO-LAB10.txt).
"""

import re
import sys
import time

from pyperplan import search
from pyperplan.planner import search_plan

from manito_api import ManitoArm

# zona -> angulo de hombro (j1), con j3=30 fijo.
ZONE_J1 = {
    "zona-a": -60,
    "zona-r": -30,
    "zona-g": 0,
    "zona-b": 30,
    "zona-izquierda": 60,
    "zona-derecha": 90,
}
J3 = 30
Z_TRAVEL = 10  # altura segura para desplazarse entre zonas
Z_TABLE = -10  # profundidad para alcanzar un cubo apoyado en la mesa
Z_STACK = -6   # profundidad para alcanzar/soltar un cubo apoyado sobre otro (+4cm)


def parse_init(problem_path):
    """Lee el :init del problema y arma una funcion item -> zona actual.

    Resuelve `(on o p)` encadenando hasta encontrar la zona base de `p`.
    Asume que la base de un `stack`/`unstack` no cambia de zona durante el
    plan (cierto para los problemas 1-5).
    """
    text = open(problem_path, encoding="utf-8").read()
    at_map = {
        k.lower(): v.lower()
        for k, v in re.findall(r"\(at\s+(\S+)\s+(\S+)\)", text, re.IGNORECASE)
    }
    on_map = {
        k.lower(): v.lower()
        for k, v in re.findall(r"\(on\s+(\S+)\s+(\S+)\)", text, re.IGNORECASE)
    }

    def zone_of(item):
        item = item.lower()
        seen = set()
        while item not in at_map:
            if item in seen or item not in on_map:
                raise ValueError(f"No se pudo resolver la zona de '{item}'")
            seen.add(item)
            item = on_map[item]
        return at_map[item]

    return zone_of


def parse_action(op_name):
    """'(pick-up a zona-a)' -> ('pick-up', ['a', 'zona-a'])"""
    tokens = op_name.strip("()").split()
    return tokens[0], tokens[1:]


def move_to(arm, zone, z):
    arm.move_joints(ZONE_J1[zone], J3, 0, z)


def run_plan(arm, plan, zone_of):
    for step, op in enumerate(plan, 1):
        name, args = parse_action(op.name)
        print(f"  {step}. {op.name}")

        if name == "pick-up":
            _, zone = args
            move_to(arm, zone, Z_TRAVEL)
            move_to(arm, zone, Z_TABLE)
            arm.gripper(True)
            move_to(arm, zone, Z_TRAVEL)

        elif name == "put-down":
            _, zone = args
            move_to(arm, zone, Z_TRAVEL)
            move_to(arm, zone, Z_TABLE)
            arm.gripper(False)
            move_to(arm, zone, Z_TRAVEL)

        elif name == "stack":
            _, base = args
            zone = zone_of(base)
            move_to(arm, zone, Z_TRAVEL)
            move_to(arm, zone, Z_STACK)
            arm.gripper(False)
            move_to(arm, zone, Z_TRAVEL)

        elif name == "unstack":
            _, base = args
            zone = zone_of(base)
            move_to(arm, zone, Z_TRAVEL)
            move_to(arm, zone, Z_STACK)
            arm.gripper(True)
            move_to(arm, zone, Z_TRAVEL)

        else:
            raise ValueError(f"Accion desconocida: {name}")


def main():
    if len(sys.argv) < 3:
        print("Uso: uv run python agente.py <domain.pddl> <problema.pddl> [url]")
        sys.exit(1)

    domain_path, problem_path = sys.argv[1], sys.argv[2]
    url = sys.argv[3] if len(sys.argv) > 3 else None

    print(f"Planificando: {problem_path}")
    t0 = time.time()
    plan = search_plan(domain_path, problem_path, search.breadth_first_search, None)
    t_plan = time.time() - t0

    if plan is None:
        print("No se encontro plan.")
        sys.exit(1)

    print(f"Plan encontrado en {t_plan:.3f}s ({len(plan)} pasos):")
    zone_of = parse_init(problem_path)
    arm = ManitoArm(url)
    arm.home()

    t0 = time.time()
    run_plan(arm, plan, zone_of)
    t_exec = time.time() - t0

    print(f"\nPlanificacion: {t_plan:.3f}s | Ejecucion: {t_exec:.3f}s | Total: {t_plan + t_exec:.3f}s")


if __name__ == "__main__":
    main()
