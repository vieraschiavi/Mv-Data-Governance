#!/usr/bin/env bash
# MV Data Governance · Lanzador para Linux / macOS.
# Crea el entorno la primera vez, instala dependencias y abre el programa.
set -euo pipefail
cd "$(dirname "$0")"

if [ ! -x ".venv/bin/python" ]; then
    echo "[ES] Primera ejecución: creando entorno... [EN] First run... [PT] Primeira execução..."
    python3 -m venv .venv
    .venv/bin/python -m pip install --upgrade pip
    .venv/bin/python -m pip install -r requirements.txt
fi

exec .venv/bin/python packaging/mvdg_launcher.py
