#!/usr/bin/env bash
# detect_stack.sh — heurística de detección de stack, sin asumir lenguaje.
# Imprime lo que encuentra y sugiere los comandos típicos. Es informativo:
# nunca modifica nada y nunca falla la operación que lo invocó.
set -u
root="${CLAUDE_PROJECT_DIR:-$(pwd)}"
cd "$root" 2>/dev/null || exit 0

found=0
say() { printf '  - %s\n' "$1"; found=1; }
# has_glob PATTERN → éxito solo si el patrón matchea algún archivo real.
# (evita el falso positivo de `ls glob | head`, que siempre sale 0.)
has_glob() { compgen -G "$1" >/dev/null 2>&1; }

echo "Stack detectado en: $root"

# --- Node / JS / TS ---
if [ -f package.json ]; then
  say "Node.js (package.json)"
  if grep -q '"test"' package.json 2>/dev/null;  then say "  test:  npm test"; fi
  if grep -q '"lint"' package.json 2>/dev/null;  then say "  lint:  npm run lint"; fi
  if grep -q '"build"' package.json 2>/dev/null; then say "  build: npm run build"; fi
  [ -f pnpm-lock.yaml ] && say "  gestor: pnpm"
  [ -f yarn.lock ] && say "  gestor: yarn"
fi

# --- Python ---
if [ -f pyproject.toml ] || [ -f requirements.txt ] || [ -f setup.py ]; then
  say "Python (pyproject/requirements/setup)"
  { [ -d tests ] || has_glob 'test_*.py' || has_glob '*_test.py'; } \
    && say "  test:  pytest"
  [ -f pyproject.toml ] && grep -qi 'ruff' pyproject.toml 2>/dev/null && say "  lint:  ruff check ."
fi

# --- R ---
if [ -f DESCRIPTION ] || has_glob '*.R' || has_glob '*.Rproj'; then
  say "R (DESCRIPTION/*.R)"
  [ -d tests/testthat ] && say "  test:  Rscript -e 'testthat::test_dir(\"tests/testthat\")'"
fi

# --- Go / Rust / Java ---
[ -f go.mod ]     && say "Go (go.mod) — test: go test ./...  build: go build ./..."
[ -f Cargo.toml ] && say "Rust (Cargo.toml) — test: cargo test  build: cargo build"
{ [ -f pom.xml ] || [ -f build.gradle ]; } && say "JVM (maven/gradle)"

# --- Genéricos ---
[ -f Makefile ]       && say "Makefile — mirá 'make help' o los targets test/build/lint"
[ -f docker-compose.yml ] && say "docker-compose.yml presente"
[ -d .github/workflows ] && say "CI en .github/workflows (fuente de verdad de los comandos reales)"

if [ "$found" -eq 0 ]; then
  echo "  (no se detectó un stack conocido — preguntá al usuario los comandos"
  echo "   de instalar/correr/testear/build y anotalos en CLAUDE.md)"
fi
exit 0
