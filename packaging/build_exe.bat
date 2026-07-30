@echo off
rem ============================================================
rem  MV Data Governance - Constructor del ejecutable Windows
rem  ES: Genera dist\MVDataGovernance\MVDataGovernance.exe con
rem      PyInstaller y, si Inno Setup esta instalado, tambien el
rem      instalador dist\MVDataGovernance_Setup_v<version>.exe.
rem  EN: Builds dist\MVDataGovernance\MVDataGovernance.exe with
rem      PyInstaller and, if Inno Setup is installed, also the
rem      dist\MVDataGovernance_Setup_v<version>.exe installer.
rem  PT: Gera dist\MVDataGovernance\MVDataGovernance.exe com
rem      PyInstaller e, se o Inno Setup estiver instalado, tambem
rem      o instalador dist\MVDataGovernance_Setup_v<version>.exe.
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
".venv\Scripts\python.exe" -m pip install -r requirements.txt pyinstaller cython
if errorlevel 1 goto errdeps

echo.
echo  [1/3] Cython: compilando el motor a binario (.pyd)...
rem Sin esto, mvdg\ viaja como .py en texto plano dentro del .exe (Streamlit
rem corre app.py como script, asi que PyInstaller lo copia tal cual, y el
rem cliente se queda con el motor legible en el Bloc de notas). No es
rem bloqueante: si falta Cython o el compilador de C, se avisa y se sigue con
rem el motor sin compilar. En Windows requiere Build Tools de Visual Studio.
".venv\Scripts\python.exe" packaging\build_compiled.py
if errorlevel 1 echo  AVISO: el motor NO se compilo; se empaqueta como codigo fuente legible.

echo.
echo  [2/3] PyInstaller: empaquetando el programa standalone...
".venv\Scripts\python.exe" -m PyInstaller packaging\mvdg.spec --noconfirm
if errorlevel 1 goto errbuild
echo  OK: dist\MVDataGovernance\MVDataGovernance.exe

echo.
echo  [3/3] Inno Setup: creando el instalador (opcional)...
set "ISCC="
if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles%\Inno Setup 6\ISCC.exe"
if not defined ISCC goto noiscc

rem Version real del programa (mvdg.__version__), no un numero pisado a
rem mano: asi el instalador y el build_release.py (que busca el .exe por
rem nombre) siempre coinciden con lo que efectivamente se empaqueto.
set "MVDGVER="
for /f "delims=" %%V in ('".venv\Scripts\python.exe" -c "import mvdg; print(mvdg.__version__)" 2^>nul') do set "MVDGVER=%%V"
if not defined MVDGVER set "MVDGVER=1.1.0"

"%ISCC%" /DAppVersion=%MVDGVER% packaging\instalador.iss
if errorlevel 1 goto erriscc
echo  OK: dist\MVDataGovernance_Setup_v%MVDGVER%.exe
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
