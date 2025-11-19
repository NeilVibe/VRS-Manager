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
#define MyAppVersion "1.120.0"
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
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes

; Output
OutputDir=installer_output
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
PrivilegesRequired=admin
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
Source: "..\dist_light\VRSManager.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\dist_light\_internal\*"; DestDir: "{app}\_internal"; Flags: ignoreversion recursesubdirs createallsubdirs

; Documentation
Source: "..\docs\*"; DestDir: "{app}\docs"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\BERT_MODEL_SETUP.md"; DestDir: "{app}"; Flags: ignoreversion
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
var
  InfoPage: TOutputMsgMemoWizardPage;
begin
  // Create custom info page
  InfoPage := CreateOutputMsgMemoPage(wpWelcome,
    'VRS Manager LIGHT Version',
    'Fast & Lightweight Translation Tool',
    'You are installing the LIGHT version of VRS Manager.' + #13#10 + #13#10 +
    'Features included:' + #13#10 +
    '  ✓ All VRS Check processes (Raw, Working, AllLang, Master)' + #13#10 +
    '  ✓ Punctuation/Space change detection' + #13#10 +
    '  ✓ StrOrigin Analysis sheet creation' + #13#10 +
    '  ✓ Fast, lightweight processing' + #13#10 + #13#10 +
    'LIGHT version behavior:' + #13#10 +
    '  • Punctuation-only changes: "Punctuation/Space Change"' + #13#10 +
    '  • Content changes: "Content Change"' + #13#10 + #13#10 +
    'Download size: ~150 MB' + #13#10 +
    'Installed size: ~200 MB' + #13#10 + #13#10 +
    'For AI-powered semantic similarity (FULL version):' + #13#10 +
    'Download VRSManager_v1.120.0_Full_Setup.exe instead' + #13#10 +
    '(2.6 GB download with BERT analysis)'
  );
end;
