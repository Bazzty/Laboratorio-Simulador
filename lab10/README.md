# Lab 10 — Agente manito

Dominio PDDL compartido + problemas 1-5 (autor: este equipo, mitad 1) que
mueven/apilan cubos entre zonas con el brazo Manito, y `agente.py`, que
traduce el plan encontrado por `pyperplan` en movimientos reales sobre el
simulador 3D del profesor (Genesis).

## Estructura

- `domain.pddl` — dominio compartido con el compañero (problemas 6-10 los
  agrega él sobre el mismo dominio).
- `problems/problem_1.pddl` .. `problem_5.pddl` — nuestros 5 problemas.
- `solve.py` — corre `pyperplan` sobre un domain+problem y solo imprime el
  plan (sin tocar el simulador). Útil para verificar rápido que un problema
  tiene solución.
- `agente.py` — resuelve el plan y lo ejecuta contra el simulador real vía
  `manito_api.ManitoArm` (`move_joints`/`gripper`). Mide tiempo de
  planificación y de ejecución.

## 1. Verificar un plan sin simulador

```bash
uv run python solve.py domain.pddl problems/problem_1.pddl
```

## 2. Levantar el simulador (genesis-sim)

`genesis-sim/` y `py-api/` son el simulador del profesor, provisto tal cual
— no se modifican ni se entregan junto con `lab10/`. Instrucciones de
instalación completas en `genesis-sim/README.md`; en resumen, con el
simulador instalado y sus dependencias sincronizadas (`uv sync` dentro de
`genesis-sim/`):

```bash
cd genesis-sim
uv run simctl viewer configs/scenarios/scene_1.yml --api
# o headless, sin ventana:
uv run simctl serve configs/scenarios/scene_1.yml
```

Cada `problem_N.pddl` tiene su escenario correspondiente en
`genesis-sim/configs/scenarios/scene_N.yml` (mismas posiciones de cubos que
el `:init` del problema).

**Nota para quien no tenga acceso SSH al repo privado del profesor
(`gitea.liria.cl`):** `genesis-sim/pyproject.toml` declara `manito-api`
como dependencia remota por git+ssh. Si `uv sync` falla por eso, es un
problema de acceso al repo, no del dominio/problemas — pídele acceso al
profesor o, como workaround local (NO para entregar, solo para poder
probar en tu máquina), cambia esa línea para apuntar a la copia local de
`py-api/`:

```toml
[tool.uv.sources]
manito-api = { path = "../py-api" }
```

y ajusta el pin de `torch`/`torchvision` si tu GPU no coincide con la
versión de CUDA que trae fijada (`torch==2.9.1+cu128` en el original).
Esto es un ajuste de entorno local, no una modificación del simulador en
sí — no toca `Dockerfile`, `docker-compose.yml` ni el código fuente de
`genesis-sim/src/`.

## 3. Ejecutar un problema contra el simulador

Con el simulador corriendo (paso 2) y escuchando en, por ejemplo,
`http://localhost:8000`:

```bash
uv run python agente.py domain.pddl problems/problem_2.pddl http://localhost:8000
```

`agente.py` es genérico: no cambia entre problemas, solo recibe qué
`problem_N.pddl` correr contra el escenario que esté cargado en ese
momento en el simulador. La tabla `ZONE_J1` (zona → ángulo de hombro del
brazo) fue calibrada probando valores simples de `move_joints` contra el
simulador (mismo estilo que `py-api/examples/pick_cube.py`), sin resolver
cinemática inversa.

## 4. Reproducibilidad (antes de comprimir la entrega)

```bash
rm -rf .venv
uv sync
uv run python solve.py domain.pddl problems/problem_1.pddl   # repetir por cada problema
```

Los 5 problemas fueron corridos y validados contra sus 5 escenarios
(cada cubo termina en la zona/apilado del `:goal`, verificado leyendo
`/api/v1/state` del simulador tras la ejecución).
