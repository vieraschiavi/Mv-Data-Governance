---
description: Escanea el repo y reporta cuáles de las 12 capacidades de Claude Code están configuradas y cuáles faltan, cada una con el comando exacto para cerrar el gap.
allowed-tools: Read, Grep, Glob, Bash
disable-model-invocation: false
---

Auditá el estado de automatización de este repositorio. Para cada capacidad,
verificá evidencia concreta en el repo y marcá ✅ configurada / ⚠️ parcial /
❌ falta, con una línea de por qué y el comando para cerrarla.

Chequeos a hacer (buscá la evidencia, no la asumas):

1. **CLAUDE.md** — ¿existe en la raíz? ¿tiene comandos de correr/testear/build?
   → si falta: `/automate-init`.
2. **Permisos** — ¿existe `.claude/settings.json` con `permissions.allow` y
   `permissions.deny`? ¿el `deny` cubre lo irreversible? → si falta:
   `/automate-init`.
3. **Plan mode** — ¿el equipo usa planificación previa? (convención, no archivo)
   → recordá `/automate-plan <objetivo>`.
4. **Checkpoints** — ¿hay tags `automate/checkpoint-*` o convención de commits de
   checkpoint? → se generan en `/automate-build`.
5. **Skills** — ¿hay `.claude/skills/` o plugins con skills instalados?
6. **Hooks** — ¿`.claude/settings.json` o un plugin definen hooks de
   formato/tests? → si falta: `/automate-init`.
7. **MCP** — ¿qué servidores MCP hay disponibles en la sesión? ¿alguno útil sin
   conectar (GitHub, la base de datos del repo)?
8. **Plugins** — ¿este plugin (`project-automator`) está instalado? ¿hay otros?
9-10. **Context / Compact** — recordatorio de práctica: sub-agentes para lo
   pesado, compactar en trabajos largos (no es archivo).
11. **Slash commands** — ¿están disponibles los `/automate-*`? ¿hay comandos
   propios del repo en `.claude/commands/`?
12. **Sub-agentes** — ¿hay `.claude/agents/` o el plugin provee `repo-explorer`?

## Salida

Una tabla con las 12 filas (capacidad · estado · evidencia · cómo cerrar el
gap), y abajo un veredicto corto: ¿está el repo listo para que Claude trabaje
solo, o qué falta primero? Priorizá los gaps por impacto (CLAUDE.md y permisos
son los que más habilitan autonomía).
