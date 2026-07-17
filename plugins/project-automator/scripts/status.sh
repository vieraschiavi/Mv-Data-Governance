#!/usr/bin/env bash
# status.sh — resumen corto del proyecto al iniciar sesión (SessionStart hook).
# Solo lectura, informativo. Nunca falla la sesión: siempre sale 0.
set -u
root="${CLAUDE_PROJECT_DIR:-$(pwd)}"
cd "$root" 2>/dev/null || exit 0

echo "── project-automator ─────────────────────────────"
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  branch="$(git rev-parse --abbrev-ref HEAD 2>/dev/null)"
  dirty="$(git status --porcelain 2>/dev/null | wc -l | tr -d ' ')"
  echo "  rama: ${branch:-?}   cambios sin commitear: ${dirty}"
  last_ckpt="$(git tag --list 'automate/checkpoint-*' 2>/dev/null | tail -1)"
  [ -n "$last_ckpt" ] && echo "  último checkpoint: $last_ckpt"
fi
[ -f CLAUDE.md ] && echo "  CLAUDE.md: ✅" || echo "  CLAUDE.md: ❌  (corré /automate-init)"
[ -f .claude/settings.json ] && echo "  permisos/hooks: ✅" || echo "  permisos/hooks: ❌  (corré /automate-init)"
echo "  fases: /automate-plan → /automate-build → /automate-ship   ·   auditar: /automate-audit"
echo "──────────────────────────────────────────────────"
exit 0
