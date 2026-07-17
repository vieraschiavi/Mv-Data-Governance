---
description: Onboarda el repositorio actual para que Claude Code trabaje solo — genera CLAUDE.md, permisos allow/deny, hooks de verificación y releva MCP, todo adaptado al stack detectado.
argument-hint: "[notas opcionales sobre el proyecto]"
allowed-tools: Read, Grep, Glob, Bash, Write, Edit
---

Sos el instalador de automatización del proyecto. Objetivo: dejar este repo en
condiciones de que Claude trabaje de forma autónoma y segura. Contexto extra del
usuario (si lo hay): $ARGUMENTS

## 1. Detectar el stack (no asumas nada)

Corré la heurística de detección y leé lo que haga falta para entender el repo:

!`bash "${CLAUDE_PLUGIN_ROOT}/scripts/detect_stack.sh"`

Complementá mirando los manifiestos que existan (`package.json`,
`pyproject.toml`, `requirements.txt`, `DESCRIPTION`, `go.mod`, `Cargo.toml`,
`pom.xml`, `Makefile`) y el README. Deducí los comandos reales de: instalar,
correr, testear, lint y build. Si alguno no se puede deducir con confianza,
**preguntá** en vez de inventar — y anotá la respuesta en CLAUDE.md.

## 2. Generar CLAUDE.md

Si ya existe un `CLAUDE.md`, respetalo: leelo y solo completá lo que falte, sin
pisar lo que el usuario ya escribió. Si no existe, partí de
`@${CLAUDE_PLUGIN_ROOT}/templates/CLAUDE.md` y completalo con lo detectado:
qué es el proyecto, comandos de instalar/correr/testear/lint/build, convenciones
observadas (estilo, estructura), y una sección honesta de "No tocar / cuidado"
(archivos generados, migraciones, secretos, ramas protegidas).

## 3. Generar .claude/settings.json

Partí de `@${CLAUDE_PLUGIN_ROOT}/templates/settings.json`. Adaptá:

- **`permissions.allow`**: lecturas y comandos inofensivos del stack detectado
  (p. ej. el runner de tests, el linter, `git status`/`git diff`, el gestor de
  paquetes en modo lectura). Que Claude pueda trabajar sin pedir permiso a cada
  paso en lo que es seguro.
- **`permissions.deny`**: todo lo irreversible o peligroso — `rm -rf`,
  `git push --force`, `curl … | sh`, borrar `.env`/secretos, tocar ramas
  protegidas. Esto es lo que hace segura la autonomía.
- **`hooks`**: dejá los de `templates/settings.json` (formato/tests tras editar,
  status al iniciar) apuntando a los comandos reales del stack.

No escribas ningún secreto, token ni contraseña en estos archivos. Las
credenciales viven en variables de entorno; acá solo van políticas y comandos.

## 4. Relevar MCP (no instalar sin permiso)

Reportá qué servidores MCP hay disponibles en la sesión y cuáles serían útiles
para este proyecto (GitHub para PRs, la base de datos si el repo la usa, etc.).
Sugerí, no instales por tu cuenta.

## Cierre

Mostrá un resumen de lo que quedó configurado y qué falta (enlazá a
`/automate-audit`). Recordá al usuario que puede correr `/automate-plan <objetivo>`
para arrancar el primer trabajo.
