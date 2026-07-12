@echo off
rem ============================================================
rem  MV Data Governance - Version portable para Windows (.bat)
rem  ES: Doble clic y listo: crea el entorno, instala las
rem      dependencias la primera vez y abre el programa.
rem  EN: Double-click and go: creates the environment, installs
rem      dependencies on first run and opens the program.
rem  PT: Duplo clique e pronto: cria o ambiente, instala as
rem      dependencias na primeira execucao e abre o programa.
rem ============================================================
setlocal EnableExtensions
cd /d "%~dp0"
title MV Data Governance

rem --- Buscar un Python real (evita el alias falso de Microsoft Store) ---
set "PYCMD="
python --version >nul 2>nul
if not errorlevel 1 set "PYCMD=python"
if not defined PYCMD py -3 --version >nul 2>nul
if not defined PYCMD if not errorlevel 1 set "PYCMD=py -3"
if not defined PYCMD goto nopython

if exist ".venv\Scripts\python.exe" goto verify

echo.
echo  [ES] Primera ejecucion: creando entorno e instalando dependencias (2-5 min)...
echo  [EN] First run: creating environment and installing dependencies (2-5 min)...
echo  [PT] Primeira execucao: criando ambiente e instalando dependencias (2-5 min)...
echo.
%PYCMD% -m venv .venv
if errorlevel 1 goto errvenv
".venv\Scripts\python.exe" -m pip install --upgrade pip
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto errdeps

:verify
rem --- Si una instalacion previa quedo a medias, la completa sola ---
".venv\Scripts\python.exe" -c "import streamlit, plotly, pandas, fastapi" >nul 2>nul
if not errorlevel 1 goto launch
echo.
echo  [ES] Completando una instalacion anterior interrumpida...
echo  [EN] Finishing a previously interrupted install...
echo  [PT] Concluindo uma instalacao anterior interrompida...
echo.
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto errdeps

:launch
echo.
echo  [ES] Verificando que todo funcione (auto-diagnostico)...
echo  [EN] Verifying everything works (self-check)...
echo  [PT] Verificando que tudo funciona (autodiagnostico)...
".venv\Scripts\python.exe" -m mvdg.selfcheck
echo.
echo  [ES] Abriendo MV Data Governance en tu navegador...
echo  [EN] Opening MV Data Governance in your browser...
echo  [PT] Abrindo o MV Data Governance no seu navegador...
echo.
echo  (ES: para cerrar el programa, cerra esta ventana / EN: to quit, close this window / PT: para sair, feche esta janela)
echo.
".venv\Scripts\python.exe" packaging\mvdg_launcher.py
goto end

:nopython
echo.
echo  [ES] No se encontro Python. Descargalo de https://www.python.org/downloads/
echo       e instala marcando la casilla "Add Python to PATH".
echo  [EN] Python was not found. Get it from https://www.python.org/downloads/
echo       and tick "Add Python to PATH" during setup.
echo  [PT] Python nao foi encontrado. Baixe em https://www.python.org/downloads/
echo       e marque "Add Python to PATH" na instalacao.
echo.
echo  (ES: si lo acabas de instalar, cerra y volve a abrir este .bat)
goto end

:errvenv
echo.
echo  [ES] Fallo la creacion del entorno (.venv). Proba borrar la carpeta .venv y reintentar.
echo  [EN] Environment creation failed (.venv). Try deleting the .venv folder and retry.
echo  [PT] Falha ao criar o ambiente (.venv). Tente apagar a pasta .venv e repetir.
goto end

:errdeps
echo.
echo  [ES] Fallo la instalacion de dependencias. Revisa tu conexion a internet,
echo       borra la carpeta .venv y volve a ejecutar este .bat.
echo  [EN] Dependency install failed. Check your internet connection,
echo       delete the .venv folder and run this .bat again.
echo  [PT] Falha ao instalar dependencias. Verifique sua conexao com a internet,
echo       apague a pasta .venv e execute este .bat novamente.
goto end

:end
echo.
pause
endlocal
