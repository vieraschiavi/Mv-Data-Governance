#!/usr/bin/env bash
# SessionStart hook — MV Data Governance.
# Deja el entorno listo (deps de Python) y verifica que el motor importa y la
# API/app arrancan. Tolerante a fallos de red: NO aborta la sesión si pip falla.
# Idempotente: correrlo dos veces no rompe nada.
set -euo pipefail
cd "$(git rev-parse --show-toplevel 2>/dev/null || echo .)"

log() { printf '\033[0;36m[automator]\033[0m %s\n' "$1"; }

PY="python3"; command -v python3 >/dev/null 2>&1 || PY="python"

# --- Dependencias Python (motor + app + API) ---
if [ -f requirements.txt ]; then
  log "Instalando dependencias de MV Data Governance (requirements.txt)"
  "$PY" -m pip install -q -r requirements.txt || log "pip falló (¿red?) — sigo con lo que haya instalado"
fi

# --- Dependencias de test (FastAPI TestClient necesita httpx) ---
log "Asegurando dependencias de test (pytest, httpx)"
"$PY" -m pip install -q pytest httpx || log "no pude instalar pytest/httpx — los tests podrían no correr"

# --- Verificación: el motor mvdg importa ---
if "$PY" -c "import mvdg; from mvdg import __version__; print('mvdg', __version__)" 2>/dev/null; then
  log "Motor mvdg importa OK ✔"
else
  log "aviso: no pude importar mvdg (deps incompletas). La sesión sigue."
fi

# --- Verificación: la app FastAPI para BI se construye ---
if "$PY" -c "from bi_api.main import app; print('bi_api OK')" 2>/dev/null; then
  log "API BI (bi_api) importa OK ✔"
else
  log "aviso: bi_api no importable todavía (deps incompletas). La sesión sigue."
fi

log "Entorno listo ✔  ·  app: streamlit run app/app.py  ·  api: python -m bi_api.main  ·  tests: pytest tests/ -v"
