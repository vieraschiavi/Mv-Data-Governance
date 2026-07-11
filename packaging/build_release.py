"""
MV Data Governance · Generador de paquetes de entrega (dist/*.zip).

Produce los ZIP de las dos opciones de distribución:

  Opción B (siempre): MVDataGovernance_OpcionB_Portable_v{ver}.zip
      Código completo + .bat autoinstalable. Requiere Python en destino.

  Opción A (si existe): MVDataGovernance_OpcionA_Instalador_v{ver}.zip
      Empaqueta dist/MVDataGovernance_Setup_v{ver}.exe (construido antes en
      Windows con packaging/build_exe.bat). Si el Setup.exe no existe, avisa
      cómo generarlo y sigue con la Opción B.

Uso:
    python packaging/build_release.py
"""
from __future__ import annotations

import os
import sys
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from mvdg import __version__  # noqa: E402

DIST = os.path.join(ROOT, "dist")

# Qué entra en el ZIP portable (Opción B): todo lo necesario para correr,
# sin repositorio git, sin builds previos, sin la landing de venta.
_INCLUDE_DIRS = ["app", "mvdg", "api", "assets", "docs", "packaging",
                 "distribucion", "landing", "tests"]
_INCLUDE_FILES = ["MV_DataGovernance.bat", "MV_DataGovernance_API.bat",
                  "run.sh", "requirements.txt", "README.md", ".gitattributes"]
_EXCLUDE_PARTS = {"__pycache__", ".venv", ".git", ".pytest_cache", "dist", "build"}


def _iter_files():
    for f in _INCLUDE_FILES:
        path = os.path.join(ROOT, f)
        if os.path.exists(path):
            yield path
    for d in _INCLUDE_DIRS:
        for base, dirs, files in os.walk(os.path.join(ROOT, d)):
            dirs[:] = [x for x in dirs if x not in _EXCLUDE_PARTS]
            for f in files:
                if not f.endswith((".pyc", ".pyo")):
                    yield os.path.join(base, f)


def build_option_b() -> str:
    os.makedirs(DIST, exist_ok=True)
    out = os.path.join(DIST, f"MVDataGovernance_OpcionB_Portable_v{__version__}.zip")
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for path in _iter_files():
            arc = os.path.join("MVDataGovernance",
                               os.path.relpath(path, ROOT))
            z.write(path, arc)
    return out


def build_option_a() -> str | None:
    setup = os.path.join(DIST, f"MVDataGovernance_Setup_v{__version__}.exe")
    if not os.path.exists(setup):
        return None
    out = os.path.join(DIST, f"MVDataGovernance_OpcionA_Instalador_v{__version__}.zip")
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(setup, os.path.basename(setup))
        leeme = os.path.join(ROOT, "distribucion",
                             "opcion_A_instalador_exe", "LEEME.md")
        z.write(leeme, "LEEME.md")
    return out


def main() -> None:
    b = build_option_b()
    print(f"[B] Portable .bat : {b} ({os.path.getsize(b) / 1e6:.1f} MB)")
    a = build_option_a()
    if a:
        print(f"[A] Instalador exe: {a} ({os.path.getsize(a) / 1e6:.1f} MB)")
    else:
        print("[A] Instalador exe: aun no existe dist/MVDataGovernance_Setup_"
              f"v{__version__}.exe — generalo en Windows con "
              "packaging\\build_exe.bat y volve a correr este script.")


if __name__ == "__main__":
    main()
