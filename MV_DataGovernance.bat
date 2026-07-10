@echo off
rem ============================================================
rem  MV Data Governance · Version portable para Windows (.bat)
rem  ES: Doble clic y listo: crea el entorno, instala las
rem      dependencias la primera vez y abre el programa.
rem  EN: Double-click and go: creates the environment, installs
rem      dependencies on first run and opens the program.
rem  PT: Duplo clique e pronto: cria o ambiente, instala as
rem      dependencias na primeira execucao e abre o programa.
rem ============================================================
setlocal
cd /d "%~dp0"
title MV Data Governance

where python >nul 2>nul
if errorlevel 1 (
    echo.
    echo  [ES] Python no esta instalado. Descargalo de https://www.python.org/downloads/
    echo       y marca "Add Python to PATH" durante la instalacion.
    echo  [EN] Python is not installed. Get it from https://www.python.org/downloads/
    echo       and tick "Add Python to PATH" during setup.
    echo  [PT] Python nao esta instalado. Baixe em https://www.python.org/downloads/
    echo       e marque "Add Python to PATH" na instalacao.
    echo.
    pause
    exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
    echo  [ES] Primera ejecucion: creando entorno e instalando dependencias...
    echo  [EN] First run: creating environment and installing dependencies...
    echo  [PT] Primeira execucao: criando ambiente e instalando dependencias...
    python -m venv .venv || (echo Error creando el entorno & pause & exit /b 1)
    ".venv\Scripts\python.exe" -m pip install --upgrade pip
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt || (
        echo  [ES] Fallo la instalacion de dependencias. Revisa tu conexion.
        echo  [EN] Dependency install failed. Check your connection.
        echo  [PT] Falha ao instalar dependencias. Verifique sua conexao.
        pause & exit /b 1
    )
)

echo.
echo  [ES] Abriendo MV Data Governance en tu navegador...
echo  [EN] Opening MV Data Governance in your browser...
echo  [PT] Abrindo o MV Data Governance no seu navegador...
echo.
".venv\Scripts\python.exe" packaging\mvdg_launcher.py
if errorlevel 1 pause
endlocal
