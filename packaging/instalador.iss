; MV Data Governance - Instalador Windows (Inno Setup 6) - trilingue ES/EN/PT
; Envuelve el bundle standalone de PyInstaller (dist\MVDataGovernance) en un
; instalador MVDataGovernance_Setup_vX.exe con accesos directos.
;
; Construir (en Windows, con Inno Setup instalado):
;   iscc packaging\instalador.iss
; Requiere que antes exista dist\MVDataGovernance\ (salida de PyInstaller).

#define AppName "MV Data Governance"
#ifndef AppVersion
  ; Fallback si se compila a mano (iscc packaging\instalador.iss) sin pasar
  ; /DAppVersion. El camino recomendado, packaging\build_exe.bat, SIEMPRE lo
  ; pasa leyendo mvdg.__version__ (fuente única de la versión) - ver ahí.
  #define AppVersion "1.1.0"
#endif
#define AppPublisher "MV Data Governance"
#define AppExe "MVDataGovernance.exe"

[Setup]
AppId={{D4F8A2B7-3C1E-4B9A-8E52-MVDGOV000001}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} {#AppVersion}
AppPublisher={#AppPublisher}
VersionInfoVersion={#AppVersion}
VersionInfoDescription={#AppName} Setup
VersionInfoCopyright=(c) {#AppPublisher}
; Carpeta de destino sugerida - el asistente SIEMPRE muestra la página
; "Seleccionar la carpeta de destino" (Inno Setup 6 la muestra por defecto;
; DisableDirPage=no lo deja explícito) para que el cliente pueda elegir
; otro disco/carpeta en vez de Archivos de programa, como cualquier
; instalador profesional de Windows.
DefaultDirName={autopf}\MV Data Governance
DisableDirPage=no
DefaultGroupName=MV Data Governance
DisableProgramGroupPage=yes
; Si el programa quedó abierto durante una actualización, Setup detecta el
; .exe en uso y ofrece cerrarlo antes de sobrescribir los archivos (evita
; el típico "no se pudo reemplazar MVDataGovernance.exe" a mitad de upgrade).
CloseApplications=yes
RestartApplications=yes
OutputDir=..\dist
OutputBaseFilename=MVDataGovernance_Setup_v{#AppVersion}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
MinVersion=10.0
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequiredOverridesAllowed=dialog
SetupIconFile=..\assets\brand\mv.ico
UninstallDisplayIcon={app}\{#AppExe}
UninstallDisplayName={#AppName}

[Languages]
Name: "es"; MessagesFile: "compiler:Languages\Spanish.isl"
Name: "en"; MessagesFile: "compiler:Default.isl"
Name: "pt"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: "..\dist\MVDataGovernance\*"; DestDir: "{app}"; Flags: recursesubdirs ignoreversion

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExe}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExe}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExe}"; Description: "{cm:LaunchProgram,{#AppName}}"; Flags: nowait postinstall skipifsilent
