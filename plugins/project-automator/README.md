# Project Automator — plugin de Claude Code

Empaqueta las **12 capacidades de Claude Code** en un flujo repetible que deja
cualquier repositorio listo para que Claude trabaje de forma autónoma y segura.
Se instala una vez y sirve en cualquier repo (Python, Node, R, mixto): detecta
el stack en lugar de asumirlo.

## El flujo

```
/automate-init    → onboarda el repo: CLAUDE.md, permisos allow/deny, hooks, releva MCP
/automate-plan …  → planifica (solo lectura) con un sub-agente explorador; deja un plan aprobable
/automate-build   → ejecuta el plan en loop, con checkpoint por milestone y verificación por hooks
/automate-ship    → corre el gate (tests/lint/build) y, si pasa, hace commit + PR
/automate-audit   → reporta cuáles de las 12 capacidades están configuradas y cuáles faltan
```

El skill `project-automator` es el director de orquesta: aplica la filosofía
(planificar antes de tocar, dejar puntos de retorno, verificar, delegar a
sub-agentes) aunque no tipees ningún comando.

## Instalación

Desde el repo que aloja el marketplace (`.claude-plugin/marketplace.json` en la
raíz):

```
/plugin marketplace add vieraschiavi/Mv-Data-Governance
/plugin install project-automator@mv-plugins
```

O apuntando a una copia local para probar:

```
/plugin marketplace add ./           # desde la raíz del repo
/plugin install project-automator@mv-plugins
```

Verificá con `/plugin` que aparezca instalado y habilitado.

## Qué incluye

| Componente | Archivo | Capacidad del video |
|------------|---------|---------------------|
| Skill orquestador | `skills/project-automator/SKILL.md` | 5 (Skills) |
| Comandos de fase | `commands/automate-*.md` | 11 (Slash commands) |
| Sub-agente explorador | `agents/repo-explorer.md` | 12 (Sub-agentes) |
| Hooks (status al iniciar) | `hooks/hooks.json` | 6 (Hooks) |
| Plantilla CLAUDE.md | `templates/CLAUDE.md` | 1 (CLAUDE.md) |
| Plantilla permisos+hooks | `templates/settings.json` | 2 y 6 |
| Detección de stack | `scripts/detect_stack.sh` | — |

`/automate-init` completa las plantillas con los datos reales del repo. Las
capacidades restantes (Plan Mode, Checkpoints, MCP, Plugins, Context/Compact)
las orquesta el skill dentro del flujo.

## Notas

- **Nada de secretos en el repo.** Permisos y hooks van versionados; las
  credenciales viven en variables de entorno.
- **Instalar el plugin no muta tu código.** El único hook que trae el plugin es
  informativo (muestra el estado al iniciar). Las verificaciones que reformatean
  o corren tests se agregan por repo con `/automate-init`, con vos en el loop.
- **Nombres de comando.** Según la versión de Claude Code, los comandos de un
  plugin pueden aparecer namespaceados (p. ej. `/project-automator:automate-init`).
  Mirá `/help` o el menú de comandos si `/automate-init` no autocompleta.
