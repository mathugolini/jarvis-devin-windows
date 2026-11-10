[CmdletBinding()]
param(
    [string]$InstallRoot = (Join-Path $env:LOCALAPPDATA "JarvisDevin"),
    [string]$DataRoot = (Join-Path $env:LOCALAPPDATA "JarvisDevinData"),
    [string]$PythonExe = "",
    [switch]$OnlyFiles,
    [switch]$SkipModel,
    [switch]$SkipDesktop,
    [switch]$SkipPath
)
$ErrorActionPreference = "Stop"
Set-StrictMode -Version 2.0
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
$SourceRoot = Split-Path $PSScriptRoot -Parent

function Find-Python {
    param([string]$Preferred = "")
    $Candidates = New-Object System.Collections.Generic.List[string]
    if ($Preferred) { $Candidates.Add($Preferred) }
    if (-not $Preferred) {
        $Launcher = Get-Command py.exe -ErrorAction SilentlyContinue
        if ($Launcher) {
            foreach ($Version in @("3.13", "3.12")) {
                $PreviousPreference = $ErrorActionPreference
                $ErrorActionPreference = "Continue"
                $Detected = & $Launcher.Source "-$Version" -c "import sys; print(sys.executable)" 2>$null
                $Code = $LASTEXITCODE
                $ErrorActionPreference = $PreviousPreference
                if ($Code -eq 0 -and $Detected) { $Candidates.Add([string]$Detected) }
            }
        }
        foreach ($Version in @("313", "312")) {
            $Candidates.Add((Join-Path $env:LOCALAPPDATA "Programs\Python\Python$Version\python.exe"))
        }
        $Command = Get-Command python.exe -ErrorAction SilentlyContinue
        if ($Command -and $Command.Source -notlike "*\WindowsApps\*") { $Candidates.Add($Command.Source) }
    }
    foreach ($Candidate in ($Candidates | Select-Object -Unique)) {
        if (-not (Test-Path -LiteralPath $Candidate -PathType Leaf)) { continue }
        $Detected = & $Candidate -c "import struct,sys; ok=(3,12)<=sys.version_info[:2]<(3,14) and struct.calcsize('P')==8; print(sys.executable if ok else ''); sys.exit(0 if ok else 1)"
        if ($LASTEXITCODE -eq 0 -and $Detected) { return [string]$Detected }
    }
    return $null
}

function Refresh-Path {
    $UserPath = [Environment]::GetEnvironmentVariable("Path", "User")
    $MachinePath = [Environment]::GetEnvironmentVariable("Path", "Machine")
    $env:Path = "$UserPath;$MachinePath;$env:Path"
}

function Write-Utf8 {
    param([string]$Path, [string]$Text)
    [IO.File]::WriteAllText($Path, $Text, (New-Object Text.UTF8Encoding($false)))
}

try {
    if ($env:OS -ne "Windows_NT") { throw "Este instalador e para Windows 10/11 x64." }
    $Architecture = $env:PROCESSOR_ARCHITECTURE
    if ($env:PROCESSOR_ARCHITEW6432) { $Architecture = $env:PROCESSOR_ARCHITEW6432 }
    if ($Architecture -ne "AMD64") { throw "Esta versao requer Windows x64 (Intel/AMD). ARM64 ainda nao foi validado." }
    Write-Host "Jarvis + Devin para Windows" -ForegroundColor Cyan
    Write-Host "Programa: $InstallRoot"
    Write-Host "Perfil e memorias: $DataRoot"

    $Python = Find-Python -Preferred $PythonExe
    if (-not $Python -and -not $OnlyFiles -and -not $PythonExe) {
        $Winget = Get-Command winget.exe -ErrorAction SilentlyContinue
        if (-not $Winget) { throw "Python 64 bits nao encontrado. Instale Python 3.13 ou 3.12 em python.org e execute novamente. O guia explica essa etapa." }
        Write-Host "Instalando Python 3.13 para o usuario..."
        & $Winget.Source install --id Python.Python.3.13 --exact --scope user --silent --accept-source-agreements --accept-package-agreements --disable-interactivity
        if ($LASTEXITCODE -ne 0) { throw "A instalacao do Python foi interrompida. Confira a mensagem do winget." }
        Refresh-Path
        $Python = Find-Python
    }
    if (-not $Python) { throw "Python 3.12 ou 3.13 de 64 bits nao encontrado. Execute novamente apos instalar um Python compativel." }

    New-Item -ItemType Directory -Path $InstallRoot, $DataRoot -Force | Out-Null
    $BinRoot = Join-Path $InstallRoot "bin"
    New-Item -ItemType Directory -Path $BinRoot -Force | Out-Null
    $LauncherPath = Join-Path $BinRoot "jarvis-devin.cmd"
    if (Test-Path -LiteralPath $LauncherPath) {
        $Existing = [IO.File]::ReadAllText($LauncherPath)
        if ($Existing -notmatch "jarvis-devin managed launcher") { throw "Ja existe outro programa no caminho do atalho. Nenhum atalho foi sobrescrito." }
    }
    foreach ($Folder in @("app", "scripts")) {
        New-Item -ItemType Directory -Path (Join-Path $InstallRoot $Folder) -Force | Out-Null
    }
    Copy-Item -LiteralPath (Join-Path $SourceRoot "app\jarvis.py") -Destination (Join-Path $InstallRoot "app\jarvis.py") -Force
    Copy-Item -LiteralPath (Join-Path $SourceRoot "app\windows_audio.py") -Destination (Join-Path $InstallRoot "app\windows_audio.py") -Force
    Copy-Item -LiteralPath (Join-Path $SourceRoot "scripts\speak.ps1") -Destination (Join-Path $InstallRoot "scripts\speak.ps1") -Force
    foreach ($Name in @("README.md", "GUIA-WINDOWS.md", "COMECE-AQUI.html", "VALIDACAO.md", "requirements.txt")) {
        Copy-Item -LiteralPath (Join-Path $SourceRoot $Name) -Destination (Join-Path $InstallRoot $Name) -Force
    }

    $Runtime = $Python
    if (-not $OnlyFiles) {
        $VenvRoot = Join-Path $InstallRoot ".venv"
        $Runtime = Join-Path $VenvRoot "Scripts\python.exe"
        if (-not (Test-Path -LiteralPath $Runtime)) {
            & $Python -m venv $VenvRoot
            if ($LASTEXITCODE -ne 0) { throw "Nao foi possivel preparar o ambiente Python." }
        }
        Write-Host "Preparando transcricao e microfone..."
        & $Runtime -m pip install --only-binary=:all: --requirement (Join-Path $SourceRoot "requirements.txt")
        if ($LASTEXITCODE -ne 0) { throw "Nao foi possivel instalar as dependencias de voz. Verifique a conexao e a mensagem acima." }
        & $Runtime -c "import faster_whisper, sounddevice, huggingface_hub; print('Dependencias de voz carregadas.')"
        if ($LASTEXITCODE -ne 0) { throw "O motor de voz nao carregou. Consulte a secao de dependencias no guia." }
        Refresh-Path
        $Devin = Get-Command devin.exe -ErrorAction SilentlyContinue
        if (-not $Devin) {
            $KnownDevin = Join-Path $env:LOCALAPPDATA "devin\cli\bin\devin.exe"
            if (-not (Test-Path -LiteralPath $KnownDevin)) {
                Write-Host "Instalando Devin CLI pelo instalador oficial. Ele pode solicitar o login."
                $DevinSetup = Join-Path ([IO.Path]::GetTempPath()) ("jarvis-devin-setup-" + [Guid]::NewGuid().ToString("N") + ".ps1")
                try {
                    Invoke-WebRequest -UseBasicParsing -Uri "https://static.devin.ai/cli/setup.ps1" -OutFile $DevinSetup
                    & powershell.exe -NoProfile -ExecutionPolicy RemoteSigned -File $DevinSetup
                    if ($LASTEXITCODE -ne 0) { throw "O instalador do Devin nao concluiu. Confira a mensagem acima e o guia oficial." }
                } finally {
                    if (Test-Path -LiteralPath $DevinSetup) { Remove-Item -LiteralPath $DevinSetup -Force }
                }
            }
        }
    }

    $env:JARVIS_DEVIN_HOME = $DataRoot
    $env:PYTHONUTF8 = "1"
    $AppFile = Join-Path $InstallRoot "app\jarvis.py"
    & $Runtime $AppFile init
    if ($LASTEXITCODE -ne 0) { throw "Nao foi possivel preparar o perfil." }
    $SafeRuntime = $Runtime.Replace("%", "%%")
    $SafeApp = $AppFile.Replace("%", "%%")
    $SafeData = $DataRoot.Replace("%", "%%")
    $Launcher = @"
@echo off
rem jarvis-devin managed launcher
setlocal DisableDelayedExpansion
chcp 65001 >nul
set "PYTHONUTF8=1"
set "JARVIS_DEVIN_HOME=$SafeData"
set "PATH=%LOCALAPPDATA%\devin\cli\bin;%PATH%"
"$SafeRuntime" "$SafeApp" %*
exit /b %errorlevel%
"@
    Write-Utf8 -Path $LauncherPath -Text ($Launcher.Replace("`r`n", "`n").Replace("`n", "`r`n"))

    if (-not $SkipPath) {
        $CurrentPath = [Environment]::GetEnvironmentVariable("Path", "User")
        $Entries = @($CurrentPath -split ";" | Where-Object { $_ })
        if ($Entries -notcontains $BinRoot) {
            [Environment]::SetEnvironmentVariable("Path", (($Entries + $BinRoot) -join ";"), "User")
        }
    }
    if (-not $SkipDesktop) {
        $Desktop = [Environment]::GetFolderPath("Desktop")
        if ($Desktop -and (Test-Path -LiteralPath $Desktop)) {
            $Shell = New-Object -ComObject WScript.Shell
            $Shortcut = $Shell.CreateShortcut((Join-Path $Desktop "Jarvis Devin.lnk"))
            $Shortcut.TargetPath = $LauncherPath
            $Shortcut.WorkingDirectory = Join-Path $DataRoot "workspace"
            $Shortcut.Description = "Jarvis para Devin CLI"
            $Shortcut.Save()
        }
    }
    if (-not $OnlyFiles -and -not $SkipModel) {
        & $Runtime $AppFile baixar-modelo
        if ($LASTEXITCODE -ne 0) { throw "O modelo nao terminou de baixar. Execute o instalador novamente para retomar." }
    }
    Write-Host ""
    Write-Host "Arquivos preparados." -ForegroundColor Green
    Write-Host "Abra Abrir.cmd ou o atalho Jarvis Devin na Area de Trabalho."
    Write-Host "Em um NOVO PowerShell, use: jarvis-devin"
    Write-Host "Para falar: jarvis-devin voz"
    Write-Host "Pesquisa por voz: jarvis-devin voz --pesquisa"
    Write-Host "Guia: $(Join-Path $InstallRoot 'COMECE-AQUI.html')"
    exit 0
} catch {
    Write-Host ""
    Write-Host ("Nao foi possivel concluir: " + $_.Exception.Message) -ForegroundColor Red
    exit 1
}
