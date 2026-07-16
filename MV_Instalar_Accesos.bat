@echo off
rem ============================================================
rem  MV Data Governance - Accesos directos opcionales (Windows)
rem  ES: Crea (si el cliente quiere) el acceso directo del
rem      programa en el ESCRITORIO y/o en el MENU INICIO, con su
rem      icono, apuntando a la version portable MV_DataGovernance.bat.
rem      Para quitarlos:  MV_Instalar_Accesos.bat quitar
rem  EN: Creates (if the client wants) the program shortcut on the
rem      DESKTOP and/or in the START MENU, with its icon, pointing
rem      to the portable MV_DataGovernance.bat.
rem      To remove them:  MV_Instalar_Accesos.bat quitar
rem  PT: Cria (se o cliente quiser) o atalho do programa na AREA DE
rem      TRABALHO e/ou no MENU INICIAR, com seu icone, apontando
rem      para o portatil MV_DataGovernance.bat.
rem      Para remover:  MV_Instalar_Accesos.bat quitar
rem
rem  Nota honesta sobre la BARRA DE TAREAS: desde Windows 10,
rem  Microsoft no permite que un programa se ancle solo a la barra
rem  de tareas (no hay API publica). Una vez creado el acceso
rem  directo, hace clic derecho sobre el > "Anclar a la barra de
rem  tareas" - ese paso es del usuario, a proposito de Windows.
rem
rem  Sin permisos de administrador: los accesos se crean por
rem  usuario (escritorio propio y menu inicio propio).
rem ============================================================
setlocal EnableExtensions
cd /d "%~dp0"
title MV Data Governance - accesos directos

set "TARGET=%~dp0MV_DataGovernance.bat"
set "ICON=%~dp0assets\brand\mv.ico"
set "LNKNAME=MV Data Governance.lnk"

if not exist "%TARGET%" goto notarget

if /I "%~1"=="quitar" goto remove
if /I "%~1"=="remove" goto remove
if /I "%~1"=="remover" goto remove

echo.
echo  [ES] Accesos directos de MV Data Governance - responde S (si) o N (no).
echo  [EN] MV Data Governance shortcuts - answer S (yes) or N (no).
echo  [PT] Atalhos do MV Data Governance - responda S (sim) ou N (nao).
echo.

choice /C SN /M "[ES] Crear en el ESCRITORIO? / [EN] DESKTOP? / [PT] AREA DE TRABALHO?"
if errorlevel 2 goto askstart
powershell -NoProfile -ExecutionPolicy Bypass -Command "$w=New-Object -ComObject WScript.Shell; $p=Join-Path ([Environment]::GetFolderPath('Desktop')) '%LNKNAME%'; $s=$w.CreateShortcut($p); $s.TargetPath='%TARGET%'; $s.WorkingDirectory='%~dp0.'; $s.IconLocation='%ICON%'; $s.Description='MV Data Governance'; $s.Save()"
if errorlevel 1 goto errps
echo  OK: escritorio / desktop / area de trabalho

:askstart
choice /C SN /M "[ES] Crear en el MENU INICIO? / [EN] START MENU? / [PT] MENU INICIAR?"
if errorlevel 2 goto pinnote
powershell -NoProfile -ExecutionPolicy Bypass -Command "$w=New-Object -ComObject WScript.Shell; $p=Join-Path ([Environment]::GetFolderPath('Programs')) '%LNKNAME%'; $s=$w.CreateShortcut($p); $s.TargetPath='%TARGET%'; $s.WorkingDirectory='%~dp0.'; $s.IconLocation='%ICON%'; $s.Description='MV Data Governance'; $s.Save()"
if errorlevel 1 goto errps
echo  OK: menu inicio / start menu / menu iniciar

:pinnote
echo.
echo  [ES] Para la BARRA DE TAREAS: clic derecho sobre el acceso creado y
echo       elegi "Anclar a la barra de tareas" (Windows no deja que un
echo       programa se ancle solo - es una restriccion de Microsoft).
echo  [EN] For the TASKBAR: right-click the created shortcut and choose
echo       "Pin to taskbar" (Windows does not let a program pin itself).
echo  [PT] Para a BARRA DE TAREFAS: clique direito no atalho criado e
echo       escolha "Fixar na barra de tarefas".
echo.
echo  [ES] Listo. Para quitar los accesos:  MV_Instalar_Accesos.bat quitar
echo  [EN] Done. To remove the shortcuts:   MV_Instalar_Accesos.bat quitar
echo  [PT] Pronto. Para remover os atalhos: MV_Instalar_Accesos.bat quitar
goto end

:remove
powershell -NoProfile -ExecutionPolicy Bypass -Command "$d=Join-Path ([Environment]::GetFolderPath('Desktop')) '%LNKNAME%'; $m=Join-Path ([Environment]::GetFolderPath('Programs')) '%LNKNAME%'; Remove-Item -LiteralPath $d,$m -ErrorAction SilentlyContinue"
echo.
echo  [ES] Accesos directos quitados (escritorio y menu inicio).
echo  [EN] Shortcuts removed (desktop and start menu).
echo  [PT] Atalhos removidos (area de trabalho e menu iniciar).
goto end

:notarget
echo.
echo  [ES] No se encontro MV_DataGovernance.bat en esta carpeta - corre este
echo       archivo desde la carpeta del programa.
echo  [EN] MV_DataGovernance.bat was not found in this folder - run this
echo       file from the program folder.
echo  [PT] MV_DataGovernance.bat nao foi encontrado nesta pasta - execute
echo       este arquivo da pasta do programa.
goto end

:errps
echo.
echo  [ES] PowerShell fallo creando el acceso directo. Proba de nuevo o crea
echo       el acceso a mano (clic derecho en MV_DataGovernance.bat ^> Enviar
echo       a ^> Escritorio).
echo  [EN] PowerShell failed creating the shortcut. Try again or create it
echo       by hand (right-click MV_DataGovernance.bat ^> Send to ^> Desktop).
echo  [PT] O PowerShell falhou ao criar o atalho. Tente de novo ou crie o
echo       atalho manualmente.

:end
echo.
pause
