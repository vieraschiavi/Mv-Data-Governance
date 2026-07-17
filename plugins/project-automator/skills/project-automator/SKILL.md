---
name: project-automator
description: >-
  Convierte cualquier repositorio en un proyecto donde Claude Code trabaja de
  forma autónoma y segura, combinando las 12 capacidades de Claude Code
  (CLAUDE.md, permisos, plan mode, checkpoints, skills, hooks, MCP, plugins,
  manejo de contexto/compact, slash commands y sub-agentes) en un solo flujo
  repetible. Usar SIEMPRE que el usuario quiera "automatizar un proyecto",
  "preparar el repo para que Claude trabaje solo", "dejar el proyecto listo para
  producción", "arrancar un proyecto nuevo con buenas bases", o invoque los
  comandos /automate-init, /automate-plan, /automate-build, /automate-ship o
  /automate-audit. También activar cuando el usuario pida montar CLAUDE.md,
  permisos allow/deny, hooks de tests/lint, checkpoints de rollback, delegar
  exploración a sub-agentes, o llevar un cambio de idea a PR sin babysitting.
  Es genérico: detecta el stack (Python, Node, R, etc.) en vez de asumirlo.
---

# Project Automator

Un repositorio no se "automatiza" por tener muchas features encendidas, sino
por estar en un **estado donde Claude puede trabajar solo con riesgo acotado**:
sabe qué es el proyecto, tiene permiso para las acciones seguras, planifica
antes de tocar código, deja puntos de retorno, verifica lo que hace y solo
molesta al humano en las decisiones que de verdad son suyas.

Este skill es el director de orquesta de las 12 capacidades de Claude Code.
No las explica en abstracto: las encadena en un ciclo de vida repetible que
sirve en cualquier repo (Python, Node, R, mezcla). Los comandos
`/automate-*` son atajos a cada fase; este skill es la filosofía que los
sostiene y que aplica aunque el usuario nunca tipee un comando.

## Las 12 capacidades y para qué sirve cada una acá

| # | Capacidad | Rol en la automatización |
|---|-----------|--------------------------|
| 1 | CLAUDE.md | Memoria del proyecto: qué es, cómo se corre, cómo se testea, qué no tocar |
| 2 | Permisos (allow/deny) | Dejar correr las acciones seguras sin pedir permiso a cada paso |
| 3 | Plan Mode | Pensar (solo lectura) antes de escribir código |
| 4 | Checkpoints | Puntos de retorno A→B→C→D para deshacer sin miedo |
| 5 | Skills | Capacidades reutilizables (esta misma es una) |
| 6 | Hooks | Acciones automáticas en eventos: tests, lint, formato, status |
| 7 | MCP | Conectar Figma, Slack, GitHub, Notion, bases de datos |
| 8 | Plugins | Empaquetar todo e instalarlo en cualquier repo desde un marketplace |
| 9-10 | Context / Compact | Mantener el contexto liviano en trabajos largos |
| 11 | Slash commands | Los atajos `/automate-*` de cada fase |
| 12 | Sub-agentes | Exploración pesada y trabajo en paralelo sin ensuciar el contexto |

## El ciclo de vida

```
  /automate-init      →   /automate-plan   →   /automate-build   →  /automate-ship
  (una vez por repo)      (por objetivo)       (loop autónomo)       (verificar+PR)
   CLAUDE.md, permisos,    plan mode + sub-      checkpoints +          gate de tests
   hooks, detectar MCP     agente explorador     hooks tras cada edit   commit + PR

                         /automate-audit  (en cualquier momento: qué falta configurar)
```

### Fase 0 — Onboarding del repo (una vez): `/automate-init`

El objetivo es dejar el repo en condiciones de que Claude trabaje solo.
Detectá el stack real antes de asumir nada (mirá `package.json`,
`pyproject.toml`/`requirements.txt`, `*.R`/`DESCRIPTION`, `go.mod`, etc.) y
generá, adaptado a lo que encontraste:

1. **CLAUDE.md** (capacidad 1) — a partir de `templates/CLAUDE.md`, completado
   con: qué es el proyecto, comando para instalar, correr, testear y buildear,
   convenciones observadas, y una sección "No tocar / cuidado" honesta.
2. **`.claude/settings.json`** (capacidades 2 y 6) — a partir de
   `templates/settings.json`: lista `allow` con las lecturas y comandos de test
   inofensivos del stack detectado, lista `deny` con lo irreversible
   (`rm -rf`, `git push --force`, `curl | sh`, borrar `.env`), y hooks que
   corren formato/tests después de editar y muestran el estado al iniciar.
3. **Relevar MCP** (capacidad 7) — reportá qué servidores MCP hay disponibles y
   sugerí los útiles para este proyecto (GitHub para PRs, la base de datos si el
   repo la usa). No los instales sin permiso.

Nunca escribas secretos en estos archivos. Los permisos y hooks van al repo;
las credenciales viven en variables de entorno.

### Fase 1 — Planificar (solo lectura): `/automate-plan <objetivo>`

Antes de tocar código, entrá en la disciplina de **plan mode** (capacidad 3):
solo leer, nada de escribir. Para explorar sin llenar el contexto principal,
delegá el barrido pesado al sub-agente `repo-explorer` (capacidad 12): que
encuentre los archivos, símbolos y patrones relevantes y devuelva un resumen,
no volcados de archivos enteros.

Entregá un plan por pasos donde cada paso tenga: qué se cambia, qué archivos,
cómo se verifica, y en qué puntos conviene dejar un **checkpoint** (capacidad
4). El humano aprueba el plan antes de que se escriba una sola línea.

### Fase 2 — Construir (loop autónomo con red): `/automate-build`

Ejecutá el plan aprobado en un loop **PLANIFICAR→EJECUTAR→VERIFICAR→CORREGIR**.
La red de seguridad es lo que lo hace autónomo sin ser temerario:

- **Checkpoint antes de cada milestone** (capacidad 4): dejá un punto de retorno
  durable con `git` (commit o tag `automate/checkpoint-<n>`) para poder volver
  A→B→C. Complementa —no reemplaza— al `/rewind` nativo de Claude Code: git
  sobrevive al reinicio de sesión y viaja con el repo.
- **Verificación por hooks** (capacidad 6): después de cada edición, los hooks
  corren formato y tests; si algo rompe, corregí antes de seguir. No avances
  sobre un árbol roto.
- **Contexto liviano** (capacidades 9-10): en trabajos largos, delegá la
  exploración a sub-agentes y compactá cuando el contexto se llene. El summary
  post-compact preserva el hilo; no hace falta cerrar antes de tiempo.
- **Preguntar solo lo que es del humano**: decisiones ambiguas, irreversibles o
  de producto se consultan; lo mecánico y verificable se hace.

### Fase 3 — Entregar: `/automate-ship`

Corré el gate completo de verificación del stack (tests, lint, build). Solo si
pasa: commit con mensaje descriptivo y PR (capacidad 7 vía MCP de GitHub, o el
mecanismo que el repo use). Si algo falla, reportá el diagnóstico en vez de
entregar roto. Un entregable con fallos se informa, no se disimula.

### Meta — Auditar: `/automate-audit`

En cualquier momento, escaneá el repo y reportá cuáles de las 12 capacidades
están configuradas y cuáles faltan, cada una con el comando exacto para
cerrar el gap. Es lo que hace legible el estado de automatización del proyecto.

## Principios que sostienen todo esto

- **Genérico, no hardcodeado.** Detectá el stack; no asumas Python porque el
  ejemplo era Python. El mismo plugin sirve para un repo de Node, uno de R o uno
  mixto. Si no podés detectar cómo se testea/buildea un repo, preguntá y anotá
  la respuesta en CLAUDE.md para no volver a preguntar.
- **Autonomía con reversibilidad, no autonomía a ciegas.** El valor no es "que
  no pregunte nunca", es "que avance solo en lo seguro y deje siempre cómo
  volver". Checkpoints y permisos `deny` son lo que permite soltar las riendas.
- **Honestidad en el gate.** Si los tests fallan, se dice con la salida real. Un
  proyecto no está "listo para producción" porque lo declaremos, sino porque el
  gate pasa y se puede mostrar que pasa.
- **Nada de inventar.** No inventes comandos de build, endpoints ni esquemas.
  Verificá en el repo o preguntá. Adivinar es exactamente lo que un harness
  disciplinado evita.
- **El contexto es un recurso.** Sub-agentes para lo pesado, compactación para
  lo largo. Traé conclusiones al hilo principal, no volcados de archivos.

## Recursos del plugin

- `commands/automate-init.md` · `automate-plan.md` · `automate-build.md` ·
  `automate-ship.md` · `automate-audit.md` — una fase cada uno.
- `agents/repo-explorer.md` — sub-agente de exploración read-only.
- `hooks/hooks.json` — hooks de ejemplo (formato/tests post-edición, status al
  iniciar) que `/automate-init` adapta al stack.
- `templates/CLAUDE.md` · `templates/settings.json` — esqueletos que
  `/automate-init` completa según el repo.
- `scripts/detect_stack.sh` — heurística de detección de stack reutilizable por
  los comandos (no asume lenguaje).
