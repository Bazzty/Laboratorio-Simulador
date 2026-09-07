import sys

from pyperplan import search
from pyperplan.planner import search_plan, write_solution


def main():
    if len(sys.argv) < 3:
        print("Uso: python solve.py <dominio.pddl> <problema.pddl>")
        sys.exit(1)

    domain_path = sys.argv[1]
    problem_path = sys.argv[2]

    print(f"Resolviendo: {problem_path}")
    plan = search_plan(domain_path, problem_path, search.breadth_first_search, None)

    if plan is None:
        print("No se encontro plan.")
        sys.exit(1)

    print(f"\nPlan ({len(plan)} pasos):")
    for i, op in enumerate(plan, 1):
        print(f"  {i}. {op.name}")

    soln_path = problem_path + ".soln"
    write_solution(plan, soln_path)
    print(f"\nGuardado en: {soln_path}")


if __name__ == "__main__":
    main()
