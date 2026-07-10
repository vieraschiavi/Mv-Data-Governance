@echo off
rem ============================================================
rem  MV Data Governance - Constructor del ejecutable Windows
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
setlocal EnableExtensions
cd /d "%~dp0.."
title MV Data Governance - build .exe

set "PYCMD="
python --version >nul 2>nul
if not errorlevel 1 set "PYCMD=python"
if not defined PYCMD py -3 --version >nul 2>nul
if not defined PYCMD if not errorlevel 1 set "PYCMD=py -3"
if not defined PYCMD goto nopython

if exist ".venv\Scripts\python.exe" goto deps
%PYCMD% -m venv .venv
if errorlevel 1 goto errvenv

:deps
".venv\Scripts\python.exe" -m pip install --upgrade pip
".venv\Scripts\python.exe" -m pip install -r requirements.txt pyinstaller
if errorlevel 1 goto errdeps

echo.
echo  [1/2] PyInstaller: empaquetando el programa standalone...
".venv\Scripts\python.exe" -m PyInstaller packaging\mvdg.spec --noconfirm
if errorlevel 1 goto errbuild
echo  OK: dist\MVDataGovernance\MVDataGovernance.exe

echo.
echo  [2/2] Inno Setup: creando el instalador (opcional)...
set "ISCC="
if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles%\Inno Setup 6\ISCC.exe"
if not defined ISCC goto noiscc
"%ISCC%" packaging\instalador.iss
if errorlevel 1 goto erriscc
echo  OK: dist\MVDataGovernance_Setup_v1.0.0.exe
goto done

:noiscc
echo  Inno Setup no esta instalado; se omite el instalador.
echo  Descargalo de https://jrsoftware.org/isdl.php para generar el Setup.exe.
echo  El programa portable ya quedo listo en dist\MVDataGovernance\.
goto done

:nopython
echo.
echo  [ES] No se encontro Python. Descargalo de https://www.python.org/downloads/
echo  [EN] Python was not found. Get it from https://www.python.org/downloads/
echo  [PT] Python nao foi encontrado. Baixe em https://www.python.org/downloads/
goto end

:errvenv
echo  Fallo la creacion del entorno (.venv) / venv creation failed.
goto end

:errdeps
echo  Fallo la instalacion de dependencias / dependency install failed.
goto end

:errbuild
echo  Fallo PyInstaller / PyInstaller failed.
goto end

:erriscc
echo  Fallo Inno Setup / Inno Setup failed.
goto end

:done
echo.
echo  Listo / Done / Pronto.

:end
echo.
pause
endlocal
