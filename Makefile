# MV Data Governance · atajos de desarrollo
#
# El objetivo de `make test` es que un checkout limpio corra la suite con UN
# solo comando: instala dependencias (runtime + test) y después testea.
#
#   make test     ← instala y corre TODA la suite (Python + JS), como el CI
#   make test-py  ← solo pytest
#   make test-js  ← solo los tests de Node (XSS de la landing), sin deps nuevas
#   make lint     ← ruff sobre todo el repo
#   make check    ← lint + tests, el gate completo antes de un commit
#   make install  ← solo dependencias
#   make app      ← levanta el dashboard Streamlit
#   make api      ← levanta la API REST para BI
#   make selfcheck← auto-diagnóstico del motor

PYTHON ?= python3
NODE ?= node

.PHONY: install test test-py test-js lint check app api selfcheck

install:
	# No se actualiza pip acá a propósito: en Pythons administrados por la
	# distro (Debian/Ubuntu) eso intenta desinstalar el pip del sistema y
	# aborta la instalación entera.
	$(PYTHON) -m pip install --quiet -r requirements-dev.txt

test-py: install
	$(PYTHON) -m pytest tests/ -v

# Sin dependencias nuevas: usa solo módulos nativos de Node (assert, fs).
# Cubre lo que pytest no puede: las funciones de escape de la landing corren
# en el navegador, no en Python. Si no hay `node` en el PATH, se avisa y se
# sigue de largo en vez de romper `make test` en una máquina sin Node — el
# CI (que sí tiene Node) es el que lo hace obligatorio de verdad.
test-js:
	@if command -v $(NODE) >/dev/null 2>&1; then \
		$(NODE) landing/security.test.js; \
	else \
		echo "⚠️  node no está en el PATH: se saltea el test de XSS de la landing."; \
		echo "    Instalá Node 18+ y corré: make test-js"; \
	fi

test: test-py test-js

lint: install
	$(PYTHON) -m ruff check .

check: lint test

app: install
	$(PYTHON) -m streamlit run app/app.py

api: install
	$(PYTHON) -m bi_api.main

selfcheck: install
	$(PYTHON) -m mvdg.selfcheck
