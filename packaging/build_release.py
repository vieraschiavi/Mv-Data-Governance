"""
MV Data Governance · Generador de paquetes de entrega (dist/*.zip).

Produce los ZIP de las dos opciones de distribución:

  Opción B (siempre): MVDataGovernance_OpcionB_Portable_v{ver}.zip
      Código completo + .bat autoinstalable. Requiere Python en destino.

  Opción A (si existe): MVDataGovernance_OpcionA_Instalador_v{ver}.zip
      Empaqueta dist/MVDataGovernance_Setup_v{ver}.exe (construido antes en
      Windows con packaging/build_exe.bat). Si el Setup.exe no existe, avisa
      cómo generarlo y sigue con la Opción B.

  Demo web (siempre): landing/descargas/MVDataGovernance_Demo_v{ver}.zip
      Paquete liviano y 100% operativo para descarga directa desde la web
      (sin la landing ni el video): solo lo necesario para correr el programa
      por cualquiera de los 3 medios (.bat, .exe, web). Lo sirve Vercel.

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
DESCARGAS = os.path.join(ROOT, "landing", "descargas")

# Qué entra en el ZIP portable (Opción B): todo lo necesario para correr,
# sin repositorio git, sin builds previos, sin la landing de venta.
_INCLUDE_DIRS = ["app", "mvdg", "bi_api", "assets", "docs", "packaging",
                 "distribucion", "landing", "tests"]
_INCLUDE_FILES = ["MV_DataGovernance.bat", "MV_DataGovernance_API.bat",
                  "MV_DataGovernance_Server.bat", "run.sh", "run_server.sh",
                  "server_authorized.txt", "requirements.txt", "README.md",
                  ".gitattributes"]
_EXCLUDE_PARTS = {"__pycache__", ".venv", ".git", ".pytest_cache", "dist", "build"}


# Paquete demo web (liviano): corre el programa por los 3 medios, sin la
# web de venta ni el video de demo (que pesan y no hacen falta para operar).
_DEMO_DIRS = ["app", "mvdg", "bi_api", "docs", "packaging", "distribucion"]
_DEMO_FILES = ["MV_DataGovernance.bat", "MV_DataGovernance_API.bat",
               "MV_DataGovernance_Server.bat", "run.sh", "run_server.sh",
               "server_authorized.txt", "requirements.txt", "README.md",
               ".gitattributes"]
# solo los iconos de marca, no el video
_DEMO_BRAND = os.path.join("assets", "brand")


def _iter_files(dirs, files, extra_dirs=()):
    for f in files:
        path = os.path.join(ROOT, f)
        if os.path.exists(path):
            yield path
    for d in list(dirs) + list(extra_dirs):
        for base, subdirs, names in os.walk(os.path.join(ROOT, d)):
            subdirs[:] = [x for x in subdirs if x not in _EXCLUDE_PARTS]
            for f in names:
                if not f.endswith((".pyc", ".pyo")):
                    yield os.path.join(base, f)


def build_option_b() -> str:
    os.makedirs(DIST, exist_ok=True)
    out = os.path.join(DIST, f"MVDataGovernance_OpcionB_Portable_v{__version__}.zip")
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for path in _iter_files(_INCLUDE_DIRS, _INCLUDE_FILES):
            arc = os.path.join("MVDataGovernance",
                               os.path.relpath(path, ROOT))
            z.write(path, arc)
    return out


def build_web_demo() -> str:
    """ZIP liviano para descarga directa desde la web (servido por Vercel)."""
    os.makedirs(DESCARGAS, exist_ok=True)
    out = os.path.join(DESCARGAS, f"MVDataGovernance_Demo_v{__version__}.zip")
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for path in _iter_files(_DEMO_DIRS, _DEMO_FILES, extra_dirs=[_DEMO_BRAND]):
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
    d = build_web_demo()
    print(f"[Web] Demo directa : {d} ({os.path.getsize(d) / 1e6:.2f} MB)")
    b = build_option_b()
    print(f"[B]   Portable .bat : {b} ({os.path.getsize(b) / 1e6:.1f} MB)")
    a = build_option_a()
    if a:
        print(f"[A]   Instalador exe: {a} ({os.path.getsize(a) / 1e6:.1f} MB)")
    else:
        print("[A]   Instalador exe: aun no existe dist/MVDataGovernance_Setup_"
              f"v{__version__}.exe — generalo en Windows con "
              "packaging\\build_exe.bat y volve a correr este script.")


if __name__ == "__main__":
    main()
