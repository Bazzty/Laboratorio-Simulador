# Contexto para la otra mitad del equipo (problemas 6-10)

Este archivo es para pegarle a tu IA de confianza y que entienda rápido qué
ya está hecho en `domain.pddl` y cómo se ejecuta contra el simulador, sin
tener que re-derivarlo desde cero.

**Ojo:** esto lo escribió una IA (Claude). Revisa contra el `domain.pddl`,
los `problem_N.pddl` y `agente.py` reales antes de confiar en algún dato
puntual (nombres exactos, números, rutas) — puede haber alucinado algo.

## El dominio (`domain.pddl`, compartido)

- Tipos: `item`, `zone`.
- Predicados: `(at ?o - item ?z - zone)`, `(clean ?z - zone)`,
  `(clear ?o - item)`, `(hand-empty)`, `(hand-pick ?o - item)`,
  `(on ?o1 - item ?o2 - item)`, `(stackable ?o - item)`.
- Acciones: `pick-up`, `put-down`, `stack`, `unstack` (pares inversos).
  `stack` exige que el objeto de abajo sea `stackable`.
- Ojo con el closed-world assumption: todo objeto usado en `:init` necesita
  `(clear ?o)` explícito si no está debajo de otro, si no `pick-up` no
  encuentra precondición cumplida y pyperplan no da plan.

## Problemas 1-5 (ya hechos)

Los 5 comparten los mismos `:objects` (`A R G B - item`,
`zona-a zona-r zona-g zona-b zona-derecha zona-izquierda - zone`) y cada
`:init` refleja el estado resultante del problema anterior (no se ejecutan
encadenados por código, es solo la historia narrativa):

1. `A` → `zona-derecha`
2. `B` → `zona-izquierda`
3. `R` → `zona-b` (la zona que dejó libre B)
4. apilar `G` sobre `B`
5. apilar `A` sobre `R`

## Escenarios del simulador (`genesis-sim/configs/scenarios/scene_N.yml`)

Un escenario por problema, con los cubos en la posición que le corresponde
según ese `:init`. Las coordenadas de zona NO se inventaron a ojo: se
encontraron probando valores simples de `move_joints` (mismo estilo que
`py-api/examples/pick_cube.py`, variando solo el ángulo de hombro `j1` con
`j3=30` y `z=-10` fijos) y leyendo dónde cae realmente la garra vía
`/api/v1/state`. Esas posiciones reales pasaron a ser las zonas:

```
zona-a          j1=-60   [0.264, 0.283, 0.72]
zona-r          j1=-30   [0.114, 0.383, 0.72]
zona-g          j1=0     [-0.068, 0.396, 0.72]
zona-b          j1=30    [-0.231, 0.316, 0.72]
zona-izquierda  j1=60    [-0.333, 0.165, 0.72]
zona-derecha    j1=90    [-0.345, -0.017, 0.72]
```

Un cubo apilado sobre otro usa el mismo x,y de la base + 0.04 en z.

**Importante:** esto se hizo así a propósito, en vez de derivar la
cinemática del brazo desde el URDF y resolver dónde debería ir cada cubo —
el simulador es del profesor, se usa tal cual, no se le "arregla" nada.
Si para tus escenarios (6-10) necesitas otra zona o coordenada, el método
es el mismo: probar `move_joints` simple y usar la posición real que da,
no calcular a mano.

## `agente.py`

Traduce el plan de `pyperplan` a llamadas `ManitoArm.move_joints`/`gripper`.
Es genérico — no cambia entre problemas, solo recibe qué `problem_N.pddl`
correr contra el escenario que esté cargado en el simulador
(`uv run python agente.py domain.pddl problems/problem_N.pddl [url]`).
Usa una tabla fija `ZONE_J1` (zona → j1) y tres alturas: `Z_TRAVEL` (subir
para desplazarse entre zonas), `Z_TABLE` (bajar para tomar/dejar un cubo en
la mesa), `Z_STACK` (bajar para apilar/desapilar, 4cm más arriba que
`Z_TABLE`). Si agregas zonas nuevas, solo hay que sumarlas a `ZONE_J1` con
su `j1` real (mismo método de prueba de arriba).

Un detalle encontrado al validar: si el camino entre dos zonas pasa por
encima de una zona con una torre de cubos apilados (barrido de `j1` de un
extremo a otro), el brazo puede derribarla si `Z_TRAVEL` queda muy bajo.
Se subió `Z_TRAVEL` a 10 para darle más despeje. Si te pasa algo similar
con tus escenarios, la solución es la misma: subir `Z_TRAVEL` un poco más,
no rediseñar el movimiento.

## Setup del simulador

`genesis-sim/README.md` trae la instalación completa. Si te falla
`uv sync` porque no tienes acceso SSH al repo privado del profesor
(`gitea.liria.cl`) del que cuelga `manito-api`, es un tema de acceso, no
del dominio — ver `lab10/README.md` sección 2 para el workaround local
(apuntar `manito-api` a la carpeta local `py-api/` en vez del remoto).

### Cómo lo levanté yo (Windows 11 + WSL2) — puede que a ti te sirva otra vía

Esto es específico de mi PC, no es "la" forma de hacerlo — si estás en
Mac/Linux o tienes otra config de Windows, probablemente te sirva más
seguir directo el `genesis-sim/README.md`. Lo dejo por si te encuentras
con los mismos síntomas:

- Docker Desktop en Windows se descartó en mi caso porque el diagnóstico
  fue que pasa la GPU para cómputo CUDA pero no para renderizado
  OpenGL/EGL (la cámara rendería por software, lentísimo). **Ese
  diagnóstico lo hizo la IA y no está 100% verificado** — puede que en tu
  máquina Docker funcione perfectamente bien, o que el problema real haya
  sido otra cosa. Si prefieres Docker, no lo descartes solo por esto:
  pruébalo tú mismo primero (`docker compose up --build` dentro de
  `genesis-sim/`) y solo si ves el mismo síntoma (video lentísimo/sin
  aceleración) vale la pena considerar la vía WSL2 de abajo.
  Usé **WSL2 con Ubuntu nativo** (`wsl --install -d Ubuntu`) en vez de
  Docker.
- Clonar/copiar `genesis-sim/` y `py-api/` a un filesystem nativo de WSL
  (ej. `~/manito-sim/`), NO dejarlo corriendo desde `/mnt/c/...`
  (especialmente si esa carpeta de Windows sincroniza con OneDrive) — ahí
  la instalación (`make install`) se vuelve extremadamente lenta por el
  puente WSL9P a NTFS.
- Antes de `uv run simctl serve|viewer`, exportar dos variables de entorno
  (sin esto corre en CPU/software rendering, se ve carguísimo):
  ```bash
  export GALLIUM_DRIVER=d3d12
  export LD_LIBRARY_PATH=/usr/lib/wsl/lib:$LD_LIBRARY_PATH
  ```
- Para que se abra la ventana nativa del visor (`simctl viewer`) necesité
  tener seteado `DISPLAY=:0` y `WAYLAND_DISPLAY=wayland-0` (WSLg ya trae
  el soporte gráfico, pero si lanzas el comando desde un script/proceso no
  interactivo estas variables no siempre se heredan solas).
- Con eso, `simctl serve`/`viewer` corren normal y quedan accesibles desde
  Windows en `http://localhost:8000` (WSL2 reenvía `localhost`
  automáticamente).
