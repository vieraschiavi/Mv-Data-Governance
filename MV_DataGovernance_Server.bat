@echo off
rem ============================================================
rem  MV Data Governance - Modo servidor web (.bat)
rem  ES: Corre el programa como servidor en la red de la empresa
rem      para que varios usuarios lo abran desde el navegador.
rem      Solo arranca en servidores autorizados por la empresa
rem      (ver server_authorized.txt o MVDG_AUTHORIZED_HOSTS).
rem  EN: Runs the program as a web server on the company network
rem      so multiple users open it from their browser. It only
rem      starts on company-authorized servers
rem      (see server_authorized.txt or MVDG_AUTHORIZED_HOSTS).
rem  PT: Roda o programa como servidor na rede da empresa para
rem      varios usuarios abrirem pelo navegador. So inicia em
rem      servidores autorizados pela empresa
rem      (veja server_authorized.txt ou MVDG_AUTHORIZED_HOSTS).
rem ============================================================
setlocal EnableExtensions
cd /d "%~dp0"
title MV Data Governance - Servidor

set "PYCMD="
python --version >nul 2>nul
if not errorlevel 1 set "PYCMD=python"
if not defined PYCMD py -3 --version >nul 2>nul
if not defined PYCMD if not errorlevel 1 set "PYCMD=py -3"

if exist ".venv\Scripts\python.exe" goto launch
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

:launch
if not defined MVDG_SERVER_PORT set "MVDG_SERVER_PORT=8501"
echo.
echo  [ES] Iniciando en modo servidor. Host/puerto: MVDG_SERVER_HOST / MVDG_SERVER_PORT
echo       (por defecto 0.0.0.0:%MVDG_SERVER_PORT%). Autorizados: server_authorized.txt o
echo       MVDG_AUTHORIZED_HOSTS. Para detener, cerra esta ventana.
echo  [EN] Starting in server mode. Host/port: MVDG_SERVER_HOST / MVDG_SERVER_PORT
echo       (default 0.0.0.0:%MVDG_SERVER_PORT%). Authorized: server_authorized.txt or
echo       MVDG_AUTHORIZED_HOSTS. To stop, close this window.
echo  [PT] Iniciando em modo servidor. Host/porta: MVDG_SERVER_HOST / MVDG_SERVER_PORT
echo       (padrao 0.0.0.0:%MVDG_SERVER_PORT%). Autorizados: server_authorized.txt ou
echo       MVDG_AUTHORIZED_HOSTS. Para parar, feche esta janela.
echo.
echo  [ES] Abrilo en el navegador: http://localhost:%MVDG_SERVER_PORT%
echo  [EN] Open it in the browser: http://localhost:%MVDG_SERVER_PORT%
echo  [PT] Abra no navegador: http://localhost:%MVDG_SERVER_PORT%
echo.
rem --- Abre el navegador tras unos segundos (ventana aparte) ---
start "" /min ".venv\Scripts\python.exe" -c "import time,webbrowser; time.sleep(6); webbrowser.open('http://localhost:%MVDG_SERVER_PORT%')"
".venv\Scripts\python.exe" -m mvdg.server
goto end

rem ------------------------------------------------------------------
rem  install_deps: instala requirements.txt con reintentos (ver la
rem  misma rutina, comentada, en MV_DataGovernance.bat).
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
echo  [EN] Python was not found. Get it from https://www.python.org/downloads/
echo  [PT] Python nao foi encontrado. Baixe em https://www.python.org/downloads/
goto end

:errvenv
echo.
echo  [ES] Fallo la creacion del entorno (.venv). Borra .venv y reintenta.
echo  [EN] Environment creation failed (.venv). Delete .venv and retry.
echo  [PT] Falha ao criar o ambiente (.venv). Apague .venv e tente de novo.
goto end

:errdeps
echo.
echo  [ES] No se pudo instalar las dependencias despues de varios intentos. Antes de
echo       reintentar: (1) cerra cualquier otra ventana de MV Data Governance que
echo       haya quedado abierta, (2) si esta carpeta esta dentro de OneDrive/Google
echo       Drive/Dropbox, pausa la sincronizacion o movela fuera de esa carpeta,
echo       (3) revisa tu conexion a internet. Despues borra .venv y reintenta.
echo  [EN] Couldn't install dependencies after several attempts. Before retrying:
echo       (1) close any other MV Data Governance window still open, (2) if this
echo       folder is inside OneDrive/Google Drive/Dropbox, pause syncing or move it
echo       outside that folder, (3) check your internet connection. Then delete
echo       .venv and retry.
echo  [PT] Nao foi possivel instalar as dependencias apos varias tentativas. Antes
echo       de tentar de novo: (1) feche qualquer outra janela do MV Data Governance
echo       ainda aberta, (2) se esta pasta esta dentro do OneDrive/Google Drive/
echo       Dropbox, pause a sincronizacao ou mova-a para fora dessa pasta,
echo       (3) verifique sua conexao com a internet. Depois apague .venv e tente de novo.
goto end

:end
echo.
pause
endlocal
