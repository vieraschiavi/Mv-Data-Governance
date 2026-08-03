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

rem --- TEMP/TMP en ESTE disco, no en el de Windows por defecto ---
rem  ES: pip escribe temporales en el TEMP del sistema, que en Windows es
rem      casi siempre C:\Users\<usuario>\AppData\Local\Temp SIN IMPORTAR en
rem      que disco pusiste esta carpeta. Si la pusiste en D:\ a proposito
rem      (poco espacio en C:, politica de IT), un TEMP que sigue apuntando
rem      a C: rompe esa eleccion en silencio - hasta que C: se queda sin
rem      espacio a mitad de una instalacion ("No space left on device").
rem  EN: pip writes temp files to the system TEMP folder, almost always
rem      C:\Users\<user>\AppData\Local\Temp NO MATTER what disk this folder
rem      is on. If you put it on D:\ on purpose, a TEMP still pointing at
rem      C: breaks that choice silently - until C: runs out of space
rem      mid-install.
if not exist ".mvdg_tmp" mkdir ".mvdg_tmp" >nul 2>nul
set "TEMP=%cd%\.mvdg_tmp"
set "TMP=%cd%\.mvdg_tmp"

rem --- Buscar un Python real (evita el alias falso de Microsoft Store) ---
set "PYCMD="
python --version >nul 2>nul
if not errorlevel 1 set "PYCMD=python"
if not defined PYCMD py -3 --version >nul 2>nul
if not defined PYCMD if not errorlevel 1 set "PYCMD=py -3"
set "MVDG_REBUILT="

rem ==================================================================
rem  ENTORNO: crear el .venv si falta, o REPARARLO si quedo a medias.
rem  ES: que exista .venv\Scripts\python.exe NO alcanza para asumir
rem      que el entorno sirve. Los dos casos reales que rompian:
rem      (1) la creacion del venv se interrumpio -> queda el
rem          interprete pero SIN pip ("No module named pip"), y
rem      (2) se actualizo/desinstalo el Python del sistema -> el venv
rem          apunta a un interprete que ya no existe y ni siquiera
rem          arranca. Antes el .bat entraba igual y reintentaba 4
rem          veces el mismo comando condenado, culpando a OneDrive.
rem ==================================================================
:ensure_env
if not exist ".venv\Scripts\python.exe" goto make_venv

rem --- (a) el interprete del venv, arranca de verdad? ---
".venv\Scripts\python.exe" -c "pass" >nul 2>nul
if errorlevel 1 (
    echo.
    echo  [ES] El entorno quedo apuntando a un Python que ya no existe
    echo       ^(pasa al actualizar o desinstalar Python^). Rehaciendolo...
    echo  [EN] The environment points to a Python that no longer exists
    echo       ^(happens when Python is upgraded or removed^). Rebuilding...
    echo  [PT] O ambiente aponta para um Python que nao existe mais
    echo       ^(acontece ao atualizar ou desinstalar o Python^). Refazendo...
    echo.
    goto rebuild_venv
)

rem --- (b) tiene pip? Si no, se repara sin borrar nada ni bajar nada ---
".venv\Scripts\python.exe" -m pip --version >nul 2>nul
if not errorlevel 1 goto verify
echo.
echo  [ES] Al entorno le falta pip ^(instalacion anterior interrumpida^). Reparando...
echo  [EN] The environment is missing pip ^(previous install was interrupted^). Repairing...
echo  [PT] Falta pip no ambiente ^(instalacao anterior interrompida^). Reparando...
echo.
".venv\Scripts\python.exe" -m ensurepip --upgrade
if not errorlevel 1 goto verify
echo.
echo  [ES] No se pudo reparar pip. Rehaciendo el entorno desde cero...
echo  [EN] Could not repair pip. Rebuilding the environment from scratch...
echo  [PT] Nao foi possivel reparar o pip. Refazendo o ambiente do zero...
echo.
goto rebuild_venv

rem --- Rehacer el venv. Solo se intenta UNA vez por ejecucion: si el
rem     entorno recien hecho tampoco sirve, el problema no es el venv. ---
:rebuild_venv
if defined MVDG_REBUILT goto errvenv
set "MVDG_REBUILT=1"
rmdir /s /q ".venv" >nul 2>nul
goto make_venv

:make_venv
if not defined PYCMD goto nopython
echo.
echo  [ES] Preparando el entorno e instalando dependencias (2-5 min)...
echo  [EN] Preparing the environment and installing dependencies (2-5 min)...
echo  [PT] Preparando o ambiente e instalando dependencias (2-5 min)...
echo.
%PYCMD% -m venv .venv
if errorlevel 1 goto errvenv
rem Cinturon y tiradores: normalmente "venv" ya deja pip adentro, pero si
rem la copia quedo incompleta esto lo completa sin bajar nada de internet.
".venv\Scripts\python.exe" -m pip --version >nul 2>nul
if errorlevel 1 ".venv\Scripts\python.exe" -m ensurepip --upgrade >nul 2>nul
call :install_deps
rem  errorlevel 2 = pip desaparecio del entorno. Se chequea ANTES que el 1
rem  porque "if errorlevel N" en cmd significa ">= N". Ese caso se repara
rem  rehaciendo el entorno, no reintentando ni mandando al usuario a
rem  pausar OneDrive.
if errorlevel 2 goto rebuild_venv
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
rem  errorlevel 2 = pip desaparecio del entorno. Se chequea ANTES que el 1
rem  porque "if errorlevel N" en cmd significa ">= N". Ese caso se repara
rem  rehaciendo el entorno, no reintentando ni mandando al usuario a
rem  pausar OneDrive.
if errorlevel 2 goto rebuild_venv
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
rem  El 2>nul importa: sin el, cuando faltaba pip su error se filtraba por
rem  stderr y el usuario veia "No module named pip" DOS veces (una de esta
rem  linea y otra de la de abajo). Actualizar pip es una mejora, no un
rem  requisito: su resultado no se chequea a proposito.
".venv\Scripts\python.exe" -m pip install --no-cache-dir --upgrade pip >nul 2>nul
".venv\Scripts\python.exe" -m pip install --no-cache-dir -r requirements.txt
if not errorlevel 1 exit /b 0
rem  Antes de culpar a OneDrive: si pip no esta, reintentar el mismo comando
rem  4 veces no lo va a resolver. Codigo distinto para que el mensaje final
rem  diga la verdad en vez de mandar a pausar la sincronizacion al pedo.
".venv\Scripts\python.exe" -m pip --version >nul 2>nul
if errorlevel 1 exit /b 2
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
echo  [ES] No se pudo preparar el entorno de Python. Suele pasar si el antivirus
echo       bloquea la creacion de archivos, si no hay espacio en disco, o si la
echo       carpeta esta en OneDrive/Drive/Dropbox sincronizando. Ya se intento
echo       rehacerlo automaticamente.
echo       ALTERNATIVA SIN PYTHON: usa el instalador MVDataGovernance_Setup.exe
echo       ^(no necesita Python ni crear entornos: instala y anda^).
echo  [EN] Could not prepare the Python environment. Usually caused by antivirus
echo       blocking file creation, no disk space, or the folder syncing with
echo       OneDrive/Drive/Dropbox. An automatic rebuild was already attempted.
echo       NO-PYTHON ALTERNATIVE: use the MVDataGovernance_Setup.exe installer
echo       ^(no Python, no environments: install and run^).
echo  [PT] Nao foi possivel preparar o ambiente Python. Costuma ser antivirus
echo       bloqueando arquivos, falta de espaco em disco, ou a pasta sincronizando
echo       com OneDrive/Drive/Dropbox. Ja se tentou refazer automaticamente.
echo       ALTERNATIVA SEM PYTHON: use o instalador MVDataGovernance_Setup.exe
echo       ^(sem Python, sem ambientes: instala e funciona^).
goto end

:errdeps
echo.
echo  [ES] No se pudieron instalar las dependencias. Causas frecuentes:
echo       (1) sin conexion a internet, (2) otra ventana del programa abierta,
echo       (3) antivirus o OneDrive/Drive/Dropbox bloqueando archivos,
echo       (4) sin espacio en el disco C: ^(revisalo aunque este carpeta
echo       este en otro disco - algunos temporales de Windows igual usan C:^).
echo       NO hace falta borrar nada a mano: el entorno se repara solo la
echo       proxima vez que abras este .bat.
echo       ALTERNATIVA SIN PYTHON: usa el instalador MVDataGovernance_Setup.exe
echo       ^(trae todo adentro: no necesita Python ni bajar dependencias^).
echo  [EN] Could not install dependencies. Common causes: (1) no internet
echo       connection, (2) another window of the program still open,
echo       (3) antivirus or OneDrive/Drive/Dropbox locking files,
echo       (4) no free space on drive C: ^(check it even if this folder is on
echo       another drive - some Windows temp files still use C:^).
echo       You do NOT need to delete anything by hand: the environment repairs
echo       itself next time you open this .bat.
echo       NO-PYTHON ALTERNATIVE: use the MVDataGovernance_Setup.exe installer
echo       ^(everything bundled: no Python, no downloads^).
echo  [PT] Nao foi possivel instalar as dependencias. Causas comuns: (1) sem
echo       conexao com a internet, (2) outra janela do programa aberta,
echo       (3) antivirus ou OneDrive/Drive/Dropbox bloqueando arquivos,
echo       (4) sem espaco no disco C: ^(verifique mesmo que esta pasta esteja
echo       em outro disco - alguns temporarios do Windows ainda usam C:^).
echo       NAO e preciso apagar nada a mao: o ambiente se repara sozinho na
echo       proxima vez que voce abrir este .bat.
echo       ALTERNATIVA SEM PYTHON: use o instalador MVDataGovernance_Setup.exe
echo       ^(tudo incluido: sem Python, sem downloads^).
goto end

:end
echo.
pause
endlocal
