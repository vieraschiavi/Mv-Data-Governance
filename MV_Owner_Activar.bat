@echo off
rem ============================================================
rem  MV Data Governance - Activacion del owner (un solo clic)
rem  ES: Genera el par de claves de licencias si falta, se firma
rem      la licencia de owner atada a ESTA PC y la activa. El
rem      programa abre desbloqueado desde la proxima vez.
rem  EN: Creates the license key pair if missing, self-signs the
rem      owner license bound to THIS PC and activates it.
rem  PT: Gera o par de chaves se faltar, assina a licenca de
rem      owner atada a ESTE PC e a ativa.
rem
rem  Corre aca y no en la nube por dos razones concretas:
rem   - la clave PRIVADA emite todas las licencias del producto y
rem     tiene que nacer y quedarse en tu equipo;
rem   - el id de maquina de un servidor no es el tuyo (y ese
rem     servidor se destruye al rato).
rem ============================================================
setlocal EnableExtensions
cd /d "%~dp0"
title MV Data Governance - Activar owner

rem --- TEMP/TMP en este disco (mismo motivo que los otros .bat) ---
if not exist ".mvdg_tmp" mkdir ".mvdg_tmp" >nul 2>nul
set "TEMP=%cd%\.mvdg_tmp"
set "TMP=%cd%\.mvdg_tmp"

rem --- Python: el del entorno del programa si existe; si no, el del sistema ---
set "PY="
if exist ".venv\Scripts\python.exe" set "PY=.venv\Scripts\python.exe"
if not defined PY (
    python --version >nul 2>nul
    if not errorlevel 1 set "PY=python"
)
if not defined PY (
    py -3 --version >nul 2>nul
    if not errorlevel 1 set "PY=py -3"
)
if not defined PY goto nopython

rem --- 'cryptography' es lo unico que hace falta para firmar ---
%PY% -c "import cryptography" >nul 2>nul
if errorlevel 1 (
    echo.
    echo  [ES] Instalando lo necesario para firmar la licencia...
    echo  [EN] Installing what's needed to sign the license...
    echo  [PT] Instalando o necessario para assinar a licenca...
    echo.
    %PY% -m pip install --no-cache-dir cryptography
    if errorlevel 1 goto errdeps
)

%PY% packaging\owner_setup.py %1
if errorlevel 1 goto errsetup
goto fin

:nopython
echo.
echo  [ES] No se encontro Python. Instalalo desde https://www.python.org/downloads/
echo       marcando "Add Python to PATH", cerra esta ventana y volve a abrir este .bat.
echo  [EN] Python was not found. Install it from https://www.python.org/downloads/
echo       ticking "Add Python to PATH", then reopen this .bat.
echo  [PT] Python nao encontrado. Instale de https://www.python.org/downloads/
echo       marcando "Add Python to PATH" e reabra este .bat.
goto fin

:errdeps
echo.
echo  [ES] No se pudo instalar 'cryptography' (revisa tu conexion a internet).
echo  [EN] Could not install 'cryptography' (check your internet connection).
echo  [PT] Nao foi possivel instalar 'cryptography' (verifique sua conexao).
goto fin

:errsetup
echo.
echo  [ES] La activacion no se completo. El detalle esta arriba.
echo  [EN] Activation did not complete. Details above.
echo  [PT] A ativacao nao foi concluida. Detalhes acima.

:fin
echo.
pause
endlocal
