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
call :install_deps
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
call :install_deps
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

rem ------------------------------------------------------------------
rem  install_deps: instala requirements.txt con reintentos.
rem  ES: en carpetas sincronizadas por OneDrive/Google Drive/Dropbox, o
rem      si quedo un proceso previo del programa abierto, pip puede
rem      fallar una vez porque otro proceso tiene el archivo abierto
rem      (WinError 32). Reintentamos unas veces antes de darnos por
rem      vencidos: casi siempre alcanza.
rem  EN: in folders synced by OneDrive/Google Drive/Dropbox, or if a
rem      previous instance of the program is still open, pip can fail
rem      once because another process has the file open (WinError 32).
rem      We retry a few times before giving up: it almost always works.
rem ------------------------------------------------------------------
:install_deps
set "MVDG_TRIES=4"
:install_deps_try
".venv\Scripts\python.exe" -m pip install --upgrade pip >nul
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if not errorlevel 1 exit /b 0
set /a MVDG_TRIES-=1
if %MVDG_TRIES% gtr 0 (
    echo.
    echo  [ES] La instalacion choco con un archivo en uso ^(comun si esta carpeta
    echo       se sincroniza con OneDrive/Google Drive/Dropbox^). Reintentando...
    echo  [EN] Install hit a file in use ^(common if this folder is synced by
    echo       OneDrive/Google Drive/Dropbox^). Retrying...
    echo  [PT] A instalacao encontrou um arquivo em uso ^(comum se esta pasta
    echo       e sincronizada pelo OneDrive/Google Drive/Dropbox^). Tentando de novo...
    timeout /t 4 /nobreak >nul
    goto install_deps_try
)
exit /b 1

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
echo  [ES] No se pudo instalar las dependencias despues de varios intentos. Antes de
echo       reintentar: (1) cerra cualquier otra ventana de MV Data Governance que
echo       haya quedado abierta, (2) si esta carpeta esta dentro de OneDrive/Google
echo       Drive/Dropbox, pausa la sincronizacion o movela fuera de esa carpeta
echo       ^(ej. C:\MVDataGovernance^), (3) revisa tu conexion a internet. Despues
echo       borra la carpeta .venv y volve a ejecutar este .bat.
echo  [EN] Couldn't install dependencies after several attempts. Before retrying:
echo       (1) close any other MV Data Governance window still open, (2) if this
echo       folder is inside OneDrive/Google Drive/Dropbox, pause syncing or move it
echo       outside that folder (e.g. C:\MVDataGovernance), (3) check your internet
echo       connection. Then delete the .venv folder and run this .bat again.
echo  [PT] Nao foi possivel instalar as dependencias apos varias tentativas. Antes
echo       de tentar de novo: (1) feche qualquer outra janela do MV Data Governance
echo       ainda aberta, (2) se esta pasta esta dentro do OneDrive/Google Drive/
echo       Dropbox, pause a sincronizacao ou mova-a para fora dessa pasta
echo       ^(ex. C:\MVDataGovernance^), (3) verifique sua conexao com a internet.
echo       Depois apague a pasta .venv e execute este .bat novamente.
goto end

:end
echo.
pause
endlocal
