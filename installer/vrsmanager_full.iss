; VRS Manager FULL Installer Script
; Inno Setup 6.0+
;
; This installer creates a FULL version of VRS Manager:
; - Core VRS Check features (all 4 processors)
; - Punctuation/Space detection for StrOrigin Analysis
; - PyTorch + BERT model for semantic similarity
; - Complete AI-powered analysis
; - Larger download (~2.6GB)
;
; Output: Shows "XX.X% similar" with BERT analysis

#define MyAppName "VRS Manager"
#define MyAppVersion "1.120.0"
#define MyAppPublisher "Neil Schmitt"
#define MyAppURL "https://github.com/NeilVibe/VRS-Manager"
#define MyAppExeName "VRSManager.exe"

[Setup]
; Application info
AppId={{9B8C4D5E-6F7A-8B9C-0D1E-2F3A4B5C6D7E}
AppName={#MyAppName} (FULL)
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion} (FULL)
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}/issues
AppUpdatesURL={#MyAppURL}/releases

; Install paths
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes

; Output
OutputDir=..\installer_output
OutputBaseFilename=VRSManager_v{#MyAppVersion}_Full_Setup
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
; Full application (includes BERT + PyTorch)
Source: "..\dist_full\VRSManager\VRSManager.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\dist_full\VRSManager\_internal\*"; DestDir: "{app}\_internal"; Flags: ignoreversion recursesubdirs createallsubdirs

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
  InfoText: String;
begin
  InfoText := 'You are installing the FULL version of VRS Manager.' + #13#10 + #13#10 +
              'Features included:' + #13#10 +
              '  ✓ All VRS Check processes (Raw, Working, AllLang, Master)' + #13#10 +
              '  ✓ Punctuation/Space change detection' + #13#10 +
              '  ✓ BERT AI semantic similarity analysis' + #13#10 +
              '  ✓ Korean language optimization (KR-SBERT)' + #13#10 +
              '  ✓ Complete offline operation' + #13#10 + #13#10 +
              'FULL version behavior:' + #13#10 +
              '  • Punctuation-only changes: "Punctuation/Space Change"' + #13#10 +
              '  • Content changes: Shows similarity percentage' + #13#10 +
              '    Example: "94.5% similar", "48.6% similar"' + #13#10 + #13#10 +
              'Download size: ~2.6 GB' + #13#10 +
              'Installed size: ~3.5 GB' + #13#10 + #13#10 +
              'Includes:' + #13#10 +
              '  • PyTorch (~2 GB)' + #13#10 +
              '  • Korean BERT Model (447 MB)' + #13#10 +
              '  • All ML dependencies' + #13#10 + #13#10 +
              'After installation, you can zip the entire folder' + #13#10 +
              'and transfer to offline computers!';

  InfoPage := CreateOutputMsgMemoPage(wpWelcome,
    'VRS Manager FULL Version',
    'Complete AI-Powered Translation Tool',
    InfoText);
end;
