#!/usr/bin/env bash
# MV Data Governance · Modo servidor web para Linux / macOS.
# Corre el programa como servidor en la red de la empresa (varios usuarios lo
# abren desde el navegador). Solo arranca en servidores autorizados por la
# empresa: definí MVDG_AUTHORIZED_HOSTS (hosts separados por coma) o creá el
# archivo server_authorized.txt (un host por línea).
#
# Host/puerto: MVDG_SERVER_HOST (por defecto 0.0.0.0) y MVDG_SERVER_PORT (8501).
set -euo pipefail
cd "$(dirname "$0")"

if [ ! -x ".venv/bin/python" ]; then
    echo "[ES] Primera ejecución: creando entorno... [EN] First run... [PT] Primeira execução..."
    python3 -m venv .venv
    .venv/bin/python -m pip install --upgrade pip
    .venv/bin/python -m pip install -r requirements.txt
fi

exec .venv/bin/python -m mvdg.server
