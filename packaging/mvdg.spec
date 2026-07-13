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
from PyInstaller.utils.hooks import collect_all

ROOT = os.path.abspath(os.getcwd())

# Dependencias que necesitan recolección completa (datos + submódulos)
_PAQUETES = [
    "streamlit", "plotly", "altair", "pandas", "numpy",
    "pyarrow", "xlsxwriter", "openpyxl",
    "fastapi", "starlette", "uvicorn",
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

# Código y recursos propios. bi_api = API REST para BI (Python/FastAPI); NO se
# incluye la carpeta api/ (funciones serverless Node.js de MercadoPago, que solo
# corren en Vercel y no forman parte del programa de escritorio).
datas += [
    (os.path.join(ROOT, "app"), "app"),
    (os.path.join(ROOT, "mvdg"), "mvdg"),
    (os.path.join(ROOT, "bi_api"), "bi_api"),
    (os.path.join(ROOT, "assets", "brand"), os.path.join("assets", "brand")),
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
