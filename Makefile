# MV Data Governance · atajos de desarrollo
#
# El objetivo de `make test` es que un checkout limpio corra la suite con UN
# solo comando: instala dependencias (runtime + test) y después testea.
#
#   make test     ← instala y corre los tests (lo que corre también el CI)
#   make lint     ← ruff sobre todo el repo
#   make check    ← lint + tests, el gate completo antes de un commit
#   make install  ← solo dependencias
#   make app      ← levanta el dashboard Streamlit
#   make api      ← levanta la API REST para BI
#   make selfcheck← auto-diagnóstico del motor

PYTHON ?= python3

.PHONY: install test lint check app api selfcheck

install:
	# No se actualiza pip acá a propósito: en Pythons administrados por la
	# distro (Debian/Ubuntu) eso intenta desinstalar el pip del sistema y
	# aborta la instalación entera.
	$(PYTHON) -m pip install --quiet -r requirements-dev.txt

test: install
	$(PYTHON) -m pytest tests/ -v

lint: install
	$(PYTHON) -m ruff check .

check: lint test

app: install
	$(PYTHON) -m streamlit run app/app.py

api: install
	$(PYTHON) -m bi_api.main

selfcheck: install
	$(PYTHON) -m mvdg.selfcheck
