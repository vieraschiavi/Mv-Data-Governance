@echo off
rem ============================================================
rem  MV Data Governance · Constructor del ejecutable Windows
rem  ES: Genera dist\MVDataGovernance\MVDataGovernance.exe con
rem      PyInstaller y, si Inno Setup esta instalado, tambien el
rem      instalador dist\MVDataGovernance_Setup_v1.0.0.exe.
rem  EN: Builds dist\MVDataGovernance\MVDataGovernance.exe with
rem      PyInstaller and, if Inno Setup is installed, also the
rem      dist\MVDataGovernance_Setup_v1.0.0.exe installer.
rem  PT: Gera dist\MVDataGovernance\MVDataGovernance.exe com
rem      PyInstaller e, se o Inno Setup estiver instalado, tambem
rem      o instalador dist\MVDataGovernance_Setup_v1.0.0.exe.
rem ============================================================
setlocal
cd /d "%~dp0.."
title MV Data Governance - build .exe

where python >nul 2>nul || (echo Python no encontrado / not found & pause & exit /b 1)

if not exist ".venv\Scripts\python.exe" (
    python -m venv .venv || (pause & exit /b 1)
)
".venv\Scripts\python.exe" -m pip install --upgrade pip
".venv\Scripts\python.exe" -m pip install -r requirements.txt pyinstaller || (pause & exit /b 1)

echo.
echo  [1/2] PyInstaller: empaquetando el programa standalone...
".venv\Scripts\python.exe" -m PyInstaller packaging\mvdg.spec --noconfirm || (
    echo  Fallo PyInstaller / PyInstaller failed & pause & exit /b 1
)
echo  OK: dist\MVDataGovernance\MVDataGovernance.exe

echo.
echo  [2/2] Inno Setup: creando el instalador (opcional)...
set "ISCC="
if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles%\Inno Setup 6\ISCC.exe"
if defined ISCC (
    "%ISCC%" packaging\instalador.iss || (echo  Fallo Inno Setup & pause & exit /b 1)
    echo  OK: dist\MVDataGovernance_Setup_v1.0.0.exe
) else (
    echo  Inno Setup no esta instalado; se omite el instalador.
    echo  Descargalo de https://jrsoftware.org/isdl.php para generar el Setup.exe.
    echo  El programa portable ya quedo listo en dist\MVDataGovernance\.
)

echo.
echo  Listo / Done / Pronto.
pause
endlocal
