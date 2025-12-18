; VRS Manager LIGHT Installer Script
; Inno Setup 6.0+
;
; This installer creates a LIGHT version of VRS Manager:
; - Core VRS Check features (all 4 processors)
; - Punctuation/Space detection for StrOrigin Analysis
; - NO PyTorch, NO BERT model
; - Smaller download (~150MB)
; - Fast installation
;
; Output: Shows "Content Change" instead of similarity %

#define MyAppName "VRS Manager"
#define MyAppVersion "12181615"
#define MyAppPublisher "Neil Schmitt"
#define MyAppURL "https://github.com/NeilVibe/VRS-Manager"
#define MyAppExeName "VRSManager.exe"

[Setup]
; Application info
AppId={{8A7B3C4D-5E6F-7A8B-9C0D-1E2F3A4B5C6D}
AppName={#MyAppName} (LIGHT)
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion} (LIGHT)
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}/issues
AppUpdatesURL={#MyAppURL}/releases

; Install paths
DefaultDirName={userdesktop}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes

; Output
OutputDir=..\installer_output
OutputBaseFilename=VRSManager_v{#MyAppVersion}_Light_Setup
SetupIconFile=..\images\vrsmanager.ico
UninstallDisplayIcon={app}\{#MyAppExeName}

; Compression
Compression=lzma2/ultra64
SolidCompression=yes
LZMAUseSeparateProcess=yes
LZMANumBlockThreads=4

; System requirements
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
MinVersion=6.1sp1

; Privileges
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog

; Misc
DisableWelcomePage=no
DisableDirPage=no
DisableReadyPage=no
DisableFinishedPage=no

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Core application (LIGHT version - no BERT)
Source: "..\dist_light\VRSManager\VRSManager.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\dist_light\VRSManager\_internal\*"; DestDir: "{app}\_internal"; Flags: ignoreversion recursesubdirs createallsubdirs

; Documentation
Source: "..\docs\*"; DestDir: "{app}\docs"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\docs\BERT_MODEL_SETUP.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\README.md"; DestDir: "{app}"; Flags: ignoreversion

; Assets
Source: "..\images\vrsmanager.ico"; DestDir: "{app}\images"; Flags: ignoreversion

; Working folders for AllLang
Source: "..\Current\README.txt"; DestDir: "{app}\Current"; Flags: ignoreversion
Source: "..\Previous\README.txt"; DestDir: "{app}\Previous"; Flags: ignoreversion

[Icons]
; Start Menu
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autoprograms}\{#MyAppName}\Documentation"; Filename: "{app}\docs"
Name: "{autoprograms}\{#MyAppName}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"

; Desktop (optional)
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
; Optionally launch after install
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Clean up generated files
Type: filesandordirs; Name: "{app}\*.xlsx"
Type: filesandordirs; Name: "{app}\*.xls"
Type: filesandordirs; Name: "{app}\*.log"

[Code]
procedure InitializeWizard();
begin
  // Simple info message - no custom page needed
end;
