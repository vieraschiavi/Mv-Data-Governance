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

if exist ".venv\Scripts\python.exe" goto launch

echo.
echo  [ES] Ejecuta primero MV_DataGovernance.bat para preparar el entorno.
echo  [EN] Run MV_DataGovernance.bat first to prepare the environment.
echo  [PT] Execute primeiro MV_DataGovernance.bat para preparar o ambiente.
goto end

:launch
echo.
echo  API + docs: http://127.0.0.1:8600/docs
echo  (ES: para detener la API, cerra esta ventana / EN: to stop, close this window / PT: para parar, feche esta janela)
echo.
".venv\Scripts\python.exe" -m api.main
goto end

:end
echo.
pause
endlocal
