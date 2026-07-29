# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec del programa standalone de MV Data Governance (Windows, onedir).
Empaqueta el intérprete Python, las dependencias (Streamlit, plotly, pandas,
FastAPI…) y el código de MV Data Governance en dist/MVDataGovernance/, que el
instalador Inno Setup (instalador.iss) convierte en MVDataGovernance_Setup.exe.

Construir (en Windows):
    pyinstaller packaging/mvdg.spec --noconfirm
o directamente:
    packaging\\build_exe.bat
"""
import os
import sys
from PyInstaller.utils.hooks import (collect_all, collect_data_files,
                                      collect_submodules, copy_metadata)

ROOT = os.path.abspath(os.getcwd())
sys.path.insert(0, ROOT)
from mvdg import __version__ as MVDG_VERSION  # noqa: E402 - fuente única de la versión

# Dependencias que necesitan recolección completa (datos + submódulos).
#
# keyring, sqlalchemy y mcp NO aparecen en el análisis estático de
# PyInstaller: mvdg_launcher.py (el único script que PyInstaller rastrea)
# solo importa streamlit; el resto del motor (mvdg/, app/) viaja como
# carpeta de datos (ver más abajo) porque Streamlit ejecuta app.py como
# script, no como import — así que sus imports internos (mvdg/connectors.py
# hace `import keyring` / `from sqlalchemy import ...` DENTRO de funciones,
# mvdg/mcp_server.py hace `from mcp.server.fastmcp import FastMCP`) son
# invisibles para el analizador. Sin collect_all acá, el .exe arranca bien
# pero los conectores de base de datos, el guardado seguro de contraseñas
# en el keyring del SO y el botón "Probar servidor MCP" fallan en runtime.
_PAQUETES = [
    "streamlit", "plotly", "altair", "pandas", "numpy",
    "pyarrow", "xlsxwriter", "openpyxl",
    "fastapi", "starlette", "uvicorn",
    "keyring", "sqlalchemy",
]
datas, binaries, hiddenimports = [], [], []
for _pkg in _PAQUETES:
    try:
        d, b, h = collect_all(_pkg)
        datas += d
        binaries += b
        hiddenimports += h
    except Exception:
        pass

# mcp aparte: collect_all("mcp") IMPORTA cada submódulo para descubrirlo, y
# mcp.cli.cli requiere 'typer' (extra opcional de "mcp[cli]" que este
# programa no usa ni declara en requirements.txt - solo usamos
# mcp.server.fastmcp como servidor stdio). Eso hacía que collect_all
# reventara con ModuleNotFoundError('typer'), el except Exception: pass de
# arriba lo tragaba en silencio, y el paquete 'mcp' completo quedaba AFUERA
# del .exe - confirmado con una build de prueba real: el botón "Probar
# servidor MCP" fallaba con "No module named 'mcp'". Acá se excluye
# mcp.cli explícitamente antes de importar nada.
try:
    hiddenimports += collect_submodules(
        "mcp", filter=lambda name: not name.startswith("mcp.cli"))
    datas += collect_data_files("mcp")
    datas += copy_metadata("mcp")
except Exception:
    pass

# keyring elige el backend del SO (en Windows, el Credential Locker) vía
# entry points de importlib.metadata; collect_all no siempre alcanza a
# preservar el .dist-info que los expone. Sin esto, keyring cae en silencio
# al backend "fail" y las contraseñas guardadas quedan solo ofuscadas en vez
# de en el vault de Windows (el programa lo tolera — ver mvdg/connectors.py,
# _keyring_usable — pero mejor que no haga falta tolerarlo).
try:
    datas += copy_metadata("keyring")
except Exception:
    pass

# Información de versión del .exe (pestaña "Detalles" del Explorador de
# Windows) — se genera acá, no se hardcodea, para que nunca quede
# desincronizada de mvdg.__version__ (la única fuente de verdad).
def _version_tuple(v: str) -> tuple[int, int, int, int]:
    parts = [int(p) for p in v.split(".")[:3] if p.isdigit()]
    while len(parts) < 3:
        parts.append(0)
    return (*parts[:3], 0)


_VT = _version_tuple(MVDG_VERSION)
_BUILD_DIR = os.path.join(ROOT, "build")
os.makedirs(_BUILD_DIR, exist_ok=True)
_VERSION_INFO_PATH = os.path.join(_BUILD_DIR, "_version_info.txt")
with open(_VERSION_INFO_PATH, "w", encoding="utf-8") as _vf:
    _vf.write(f"""# Autogenerado por packaging/mvdg.spec a partir de mvdg.__version__ - no editar a mano.
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers={_VT!r},
    prodvers={_VT!r},
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0),
  ),
  kids=[
    StringFileInfo(
      [
        StringTable(
          '040904B0',
          [StringStruct('CompanyName', 'MV Data Governance'),
           StringStruct('FileDescription', 'MV Data Governance'),
           StringStruct('FileVersion', '{MVDG_VERSION}'),
           StringStruct('InternalName', 'MVDataGovernance'),
           StringStruct('LegalCopyright', '(c) MV Data Governance'),
           StringStruct('OriginalFilename', 'MVDataGovernance.exe'),
           StringStruct('ProductName', 'MV Data Governance'),
           StringStruct('ProductVersion', '{MVDG_VERSION}')])
      ]),
    VarFileInfo([VarStruct('Translation', [1033, 1200])])
  ]
)
""")

# Código y recursos propios. bi_api = API REST para BI (Python/FastAPI); NO se
# incluye la carpeta api/ (funciones serverless Node.js de MercadoPago, que solo
# corren en Vercel y no forman parte del programa de escritorio).
datas += [
    (os.path.join(ROOT, "app"), "app"),
    (os.path.join(ROOT, "mvdg"), "mvdg"),
    (os.path.join(ROOT, "bi_api"), "bi_api"),
    (os.path.join(ROOT, "assets", "brand"), os.path.join("assets", "brand")),
    (os.path.join(ROOT, "assets", "samples"), os.path.join("assets", "samples")),
]

a = Analysis(
    [os.path.join(ROOT, "packaging", "mvdg_launcher.py")],
    pathex=[ROOT],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=["tkinter", "pytest"],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="MVDataGovernance",
    icon=os.path.join(ROOT, "assets", "brand", "mv.ico"),
    version=_VERSION_INFO_PATH,
    console=False,
    disable_windowed_traceback=False,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name="MVDataGovernance",
)
