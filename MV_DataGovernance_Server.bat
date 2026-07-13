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
".venv\Scripts\python.exe" -m pip install --upgrade pip
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto errdeps

:launch
echo.
echo  [ES] Iniciando en modo servidor. Host/puerto: MVDG_SERVER_HOST / MVDG_SERVER_PORT
echo       (por defecto 0.0.0.0:8501). Autorizados: server_authorized.txt o
echo       MVDG_AUTHORIZED_HOSTS. Para detener, cerra esta ventana.
echo  [EN] Starting in server mode. Host/port: MVDG_SERVER_HOST / MVDG_SERVER_PORT
echo       (default 0.0.0.0:8501). Authorized: server_authorized.txt or
echo       MVDG_AUTHORIZED_HOSTS. To stop, close this window.
echo  [PT] Iniciando em modo servidor. Host/porta: MVDG_SERVER_HOST / MVDG_SERVER_PORT
echo       (padrao 0.0.0.0:8501). Autorizados: server_authorized.txt ou
echo       MVDG_AUTHORIZED_HOSTS. Para parar, feche esta janela.
echo.
".venv\Scripts\python.exe" -m mvdg.server
goto end

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
echo  [ES] Fallo la instalacion de dependencias. Revisa tu conexion a internet.
echo  [EN] Dependency install failed. Check your internet connection.
echo  [PT] Falha ao instalar dependencias. Verifique sua conexao com a internet.
goto end

:end
echo.
pause
endlocal
