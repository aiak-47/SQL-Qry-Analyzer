[Setup]
AppName=SQL Query Analyzer
AppVersion=1.0
AppPublisher=aiak-47
DefaultDirName={pf}\SQL Query Analyzer
DefaultGroupName=aiak-47
OutputBaseFilename=QRYAnalyzer
Compression=lzma
SolidCompression=yes

[Files]
Source: "dist\main.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: ".\*"; DestDir: "{app}\files"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\YourAppName"; Filename: "{app}\main.exe"
Name: "{group}\Uninstall YourAppName"; Filename: "{uninstallexe}"

[Run]
Filename: "{app}\your_script.exe"; Description: "Launch SQL Query Analyzer"; Flags: nowait postinstall skipifsilent
