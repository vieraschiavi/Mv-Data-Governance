; MV Data Governance - Instalador Windows (Inno Setup 6) - trilingue ES/EN/PT
; Envuelve el bundle standalone de PyInstaller (dist\MVDataGovernance) en un
; instalador MVDataGovernance_Setup_vX.exe con accesos directos.
;
; Construir (en Windows, con Inno Setup instalado):
;   iscc packaging\instalador.iss
; Requiere que antes exista dist\MVDataGovernance\ (salida de PyInstaller).

#define AppName "MV Data Governance"
#ifndef AppVersion
  #define AppVersion "1.0.0"
#endif
#define AppPublisher "MV Data Governance"
#define AppExe "MVDataGovernance.exe"

[Setup]
AppId={{D4F8A2B7-3C1E-4B9A-8E52-MVDGOV000001}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
DefaultDirName={autopf}\MV Data Governance
DefaultGroupName=MV Data Governance
DisableProgramGroupPage=yes
OutputDir=..\dist
OutputBaseFilename=MVDataGovernance_Setup_v{#AppVersion}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequiredOverridesAllowed=dialog
SetupIconFile=..\assets\brand\mv.ico
UninstallDisplayIcon={app}\{#AppExe}

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
