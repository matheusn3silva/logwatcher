#define AppName    "LogWatcher"
#define AppVersion "2.0.0"
#define AppPublisher "Matheus Nascimento da Silva"
#define AppExe     "LogWatcher.exe"

[Setup]
AppId={{8C1F4E2A-4D31-4B77-9E2A-LOGWATCHER001}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
OutputDir=dist\installer
OutputBaseFilename=LogWatcher-Setup-{#AppVersion}
SetupIconFile=assets\logo.ico
UninstallDisplayIcon={app}\{#AppExe}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Tasks]
Name: "desktopicon"; Description: "Criar atalho na área de trabalho"; GroupDescription: "Atalhos:"

[Files]
Source: "dist\LogWatcher\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#AppName}";        Filename: "{app}\{#AppExe}"
Name: "{group}\{#AppName} (CLI)";  Filename: "{app}\LogWatcherCLI.exe"
Name: "{group}\Desinstalar {#AppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#AppName}";  Filename: "{app}\{#AppExe}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExe}"; Description: "Executar o {#AppName}"; Flags: nowait postinstall
