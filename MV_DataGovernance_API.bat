@echo off
rem ============================================================
rem  MV Data Governance - API REST para BI (.bat)
rem  ES: Levanta la API en http://127.0.0.1:8600 para conectar
rem      Power BI, Tableau, Looker, MicroStrategy, Qlik, Excel...
rem  EN: Starts the API on http://127.0.0.1:8600 to connect
rem      Power BI, Tableau, Looker, MicroStrategy, Qlik, Excel...
rem  PT: Inicia a API em http://127.0.0.1:8600 para conectar
rem      Power BI, Tableau, Looker, MicroStrategy, Qlik, Excel...
rem ============================================================
setlocal EnableExtensions
cd /d "%~dp0"
title MV Data Governance API

rem --- Buscar un Python real (evita el alias falso de Microsoft Store) ---
set "PYCMD="
python --version >nul 2>nul
if not errorlevel 1 set "PYCMD=python"
if not defined PYCMD py -3 --version >nul 2>nul
if not defined PYCMD if not errorlevel 1 set "PYCMD=py -3"

if exist ".venv\Scripts\python.exe" goto verify
if not defined PYCMD goto nopython

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
".venv\Scripts\python.exe" -c "import fastapi, uvicorn, pandas" >nul 2>nul
if not errorlevel 1 goto launch
echo.
echo  [ES] Completando una instalacion anterior interrumpida...
echo  [EN] Finishing a previously interrupted install...
echo  [PT] Concluindo uma instalacao anterior interrompida...
echo.
call :install_deps
if errorlevel 1 goto errdeps

:launch
if not defined MVDG_API_PORT set "MVDG_API_PORT=8600"
echo.
echo  [ES] API + documentacion interactiva: http://127.0.0.1:%MVDG_API_PORT%/docs
echo  [EN] API + interactive docs: http://127.0.0.1:%MVDG_API_PORT%/docs
echo  [PT] API + documentacao interativa: http://127.0.0.1:%MVDG_API_PORT%/docs
echo.
echo  (ES: para detener la API, cerra esta ventana / EN: to stop, close this window / PT: para parar, feche esta janela)
echo.
rem --- Abre el navegador en /docs tras unos segundos (ventana aparte) ---
start "" /min ".venv\Scripts\python.exe" -c "import time,webbrowser; time.sleep(5); webbrowser.open('http://127.0.0.1:%MVDG_API_PORT%/docs')"
".venv\Scripts\python.exe" -m bi_api.main
goto end

rem ------------------------------------------------------------------
rem  install_deps: instala requirements.txt con reintentos (igual que
rem  MV_DataGovernance.bat: cubre WinError 32 por OneDrive/Drive/Dropbox).
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
echo       e instala marcando la casilla "Add Python to PATH". Si acabas de
echo       instalarlo, cerra y volve a abrir este .bat.
echo  [EN] Python was not found. Get it from https://www.python.org/downloads/
echo       and tick "Add Python to PATH". If you just installed it, reopen this .bat.
echo  [PT] Python nao foi encontrado. Baixe em https://www.python.org/downloads/
echo       e marque "Add Python to PATH". Se acabou de instalar, reabra este .bat.
goto end

:errvenv
echo.
echo  [ES] Fallo la creacion del entorno (.venv). Borra la carpeta .venv y reintenta.
echo  [EN] Environment creation failed (.venv). Delete the .venv folder and retry.
echo  [PT] Falha ao criar o ambiente (.venv). Apague a pasta .venv e tente de novo.
goto end

:errdeps
echo.
echo  [ES] No se pudo instalar las dependencias despues de varios intentos. Antes de
echo       reintentar: (1) cerra otras ventanas de MV Data Governance abiertas, (2) si
echo       esta carpeta esta en OneDrive/Google Drive/Dropbox, pausa la sincronizacion
echo       o movela fuera ^(ej. C:\MVDataGovernance^), (3) revisa tu internet. Despues
echo       borra .venv y reintenta.
echo  [EN] Couldn't install dependencies after several attempts. Before retrying:
echo       (1) close other open MV Data Governance windows, (2) if this folder is in
echo       OneDrive/Google Drive/Dropbox, pause syncing or move it out, (3) check your
echo       internet. Then delete .venv and retry.
echo  [PT] Nao foi possivel instalar as dependencias. Antes de tentar de novo: (1) feche
echo       outras janelas do MV Data Governance, (2) se esta pasta esta no OneDrive/
echo       Google Drive/Dropbox, pause a sincronizacao ou mova-a para fora, (3) verifique
echo       sua internet. Depois apague .venv e tente de novo.
goto end

:end
echo.
pause
endlocal
