#define MyAppName "Cetak Gambar Massal"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Cetak Gambar Massal"
#define MyAppExeName "Cetak Gambar Massal.exe"

[Setup]
AppId={{7D8A4A5B-8E42-4E0D-9C6F-2F0A8A6B1D37}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}

SetupIconFile=icon.ico

DefaultDirName={autopf}\{#MyAppName}

OutputDir=installer
OutputBaseFilename=Setup_Cetak_Gambar_Massal

WizardStyle=modern
DisableProgramGroupPage=yes
PrivilegesRequired=admin

UninstallDisplayName={#MyAppName}
Uninstallable=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Buat shortcut di Desktop"; GroupDescription: "Shortcut tambahan:"; Flags: unchecked

[Files]
Source: "dist\Cetak Gambar Massal.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\Cetak Gambar Massal"; Filename: "{app}\Cetak Gambar Massal.exe"; IconFilename: "{app}\Cetak Gambar Massal.exe"

Name: "{autodesktop}\Cetak Gambar Massal"; Filename: "{app}\Cetak Gambar Massal.exe"; IconFilename: "{app}\Cetak Gambar Massal.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Jalankan {#MyAppName}"; Flags: nowait postinstall skipifsilent