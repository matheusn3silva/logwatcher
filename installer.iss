#define AppName      "LogWatcher"
#define AppVersion   "1.0"
#define AppPublisher "Matheus Nascimento da Silva"
#define AppExe       "LogWatcher.exe"

[Setup]
AppId={{A3F1C7D2-5B84-4E6A-9C13-7D2E8F4B6A10}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
; Usuario ESCOLHE a pasta
DisableDirPage=no
DisableProgramGroupPage=yes
OutputDir=dist\installer
OutputBaseFilename=LogWatcher-Setup-{#AppVersion}
SetupIconFile=assets\logo.ico
UninstallDisplayIcon={app}\{#AppExe}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
; Nao exige admin: instala em %LOCALAPPDATA%\Programs por padrao.
; O usuario pode escolher "Para todos os usuarios" (Program Files) e ai o UAC e pedido.
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
CloseApplications=yes

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Tasks]
Name: "desktopicon"; Description: "Criar atalho na área de trabalho"; GroupDescription: "Atalhos:"

[Dirs]
; Se instalar em Program Files (modo admin), libera escrita para usuarios comuns,
; senao logs/ e data/connections.json falhariam ao serem criados.
Name: "{app}\logs"; Permissions: users-modify; Check: IsAdminInstallMode
Name: "{app}\data"; Permissions: users-modify; Check: IsAdminInstallMode

[Files]
Source: "dist\LogWatcher\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#AppName}";       Filename: "{app}\{#AppExe}"
Name: "{group}\{#AppName} (CLI)"; Filename: "{app}\LogWatcherCLI.exe"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExe}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExe}"; Description: "Executar o {#AppName}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Arquivos criados pelo app em tempo de execucao (o desinstalador nao os conhece).
; Remova estas linhas se quiser preservar perfis/logs ao desinstalar.
Type: filesandordirs; Name: "{app}\logs"
Type: filesandordirs; Name: "{app}\data"
