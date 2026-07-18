# Estenio — Install script for Windows
#
# Usage (PowerShell as Administrator):
#   irm https://.../install.ps1 | iex
#
# Or download and run:
#   .\install.ps1
#
# This script:
#   1. Checks/installs Python 3.10+ (silent install if missing)
#   2. Checks/installs ffmpeg (downloads static build)
#   3. Creates a virtual environment and installs estenio
#   4. Adds 'estenio' to the user PATH
#
# Run as Administrator for automatic Python/ffmpeg installation.

param(
    [switch]$SkipPython,
    [switch]$SkipFfmpeg,
    [string]$InstallDir = "$env:LOCALAPPDATA\Estenio"
)

$ErrorActionPreference = "Stop"

# ── Helper functions ────────────────────────────────────────────────────────
function Write-Info  { Write-Host "[INFO]  $args" -ForegroundColor Cyan }
function Write-OK    { Write-Host "[OK]    $args" -ForegroundColor Green }
function Write-Warn  { Write-Host "[WARN]  $args" -ForegroundColor Yellow }
function Write-Error { Write-Host "[ERROR] $args" -ForegroundColor Red }

function Test-Admin {
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($identity)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# ── Python check ────────────────────────────────────────────────────────────
if (-not $SkipPython) {
    Write-Info "Verificando Python..."
    $python = $null
    foreach ($candidate in @("python3", "python")) {
        try {
            $pyExe = Get-Command $candidate -ErrorAction SilentlyContinue
            if ($pyExe) {
                $ver = & $pyExe.Source -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>$null
                if ($ver) {
                    $major, $minor = [int[]]($ver -split '\.')
                    if ($major -eq 3 -and $minor -ge 10) {
                        $python = $pyExe.Source
                        break
                    }
                }
            }
        } catch {}
    }

    if (-not $python) {
        Write-Warn "Python 3.10+ não encontrado. Baixando e instalando..."
        $pythonUrl = "https://www.python.org/ftp/python/3.12.9/python-3.12.9-amd64.exe"
        $pythonInstaller = "$env:TEMP\python-installer.exe"

        Invoke-WebRequest -Uri $pythonUrl -OutFile $pythonInstaller
        Start-Process -Wait -FilePath $pythonInstaller -ArgumentList "/quiet", "InstallAllUsers=0", "PrependPath=1", "Include_test=0"
        Remove-Item $pythonInstaller

        # Refresh PATH for the current session
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "User") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "Machine")

        $python = (Get-Command python -ErrorAction Stop).Source
    }

    Write-OK "Python encontrado: $(& $python --version)"
}

# ── pip check ───────────────────────────────────────────────────────────────
Write-Info "Atualizando pip..."
& $python -m pip install --upgrade pip --quiet
Write-OK "pip atualizado."

# ── ffmpeg check ────────────────────────────────────────────────────────────
if (-not $SkipFfmpeg) {
    $ffmpegOnPath = Get-Command ffmpeg -ErrorAction SilentlyContinue
    if ($ffmpegOnPath) {
        Write-OK "ffmpeg encontrado no PATH: $($ffmpegOnPath.Source)"
    } else {
        Write-Warn "ffmpeg não encontrado. Baixando build estática..."
        $ffmpegUrl = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
        $ffmpegZip = "$env:TEMP\ffmpeg.zip"
        $ffmpegExtract = "$env:LOCALAPPDATA\ffmpeg"

        Invoke-WebRequest -Uri $ffmpegUrl -OutFile $ffmpegZip
        Expand-Archive -Path $ffmpegZip -DestinationPath $ffmpegExtract -Force
        Remove-Item $ffmpegZip

        # Find ffmpeg.exe inside the extracted folder (versioned subfolder)
        $ffmpegExe = Get-ChildItem -Path $ffmpegExtract -Recurse -Name "ffmpeg.exe" | Select-Object -First 1
        if ($ffmpegExe) {
            $ffmpegDir = Split-Path -Parent (Join-Path $ffmpegExtract $ffmpegExe)
            # Add to user PATH permanently
            $userPath = [Environment]::GetEnvironmentVariable("Path", "User")
            if ($userPath -notlike "*$ffmpegDir*") {
                [Environment]::SetEnvironmentVariable("Path", "$userPath;$ffmpegDir", "User")
                $env:Path = "$env:Path;$ffmpegDir"
            }
            Write-OK "ffmpeg instalado em: $ffmpegDir"
        } else {
            Write-Warn "Não foi possível encontrar ffmpeg.exe no pacote. Verifique manualmente."
        }
    }
}

# ── Create virtual environment & install ────────────────────────────────────
Write-Info "Criando ambiente virtual em: $InstallDir"
New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null

$venvDir = Join-Path $InstallDir "venv"
if (-not (Test-Path $venvDir)) {
    & $python -m venv $venvDir
}

$venvPython = [IO.Path]::Combine($venvDir, "Scripts", "python.exe")

Write-Info "Instalando dependências..."
& $venvPython -m pip install --upgrade pip --quiet
& $venvPython -m pip install yt-dlp --quiet

# Install estenio
if (Test-Path "pyproject.toml") {
    Write-Info "Instalando estenio do diretório local..."
    & $venvPython -m pip install -e . --quiet
} else {
    Write-Info "Instalando estenio do GitHub..."
    & $venvPython -m pip install "https://github.com/m-calendar/estenio/archive/refs/heads/main.zip" --quiet
}

# ── Create launcher batch file ──────────────────────────────────────────────
$launcherDir = Join-Path $InstallDir "bin"
New-Item -ItemType Directory -Force -Path $launcherDir | Out-Null

$launcherBat = Join-Path $launcherDir "estenio.bat"
@"
@echo off
call "$venvDir\Scripts\activate.bat" >nul
estenio %*
"@ | Out-File -FilePath $launcherBat -Encoding ASCII

# ── Add to user PATH ────────────────────────────────────────────────────────
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($userPath -notlike "*$launcherDir*") {
    [Environment]::SetEnvironmentVariable("Path", "$userPath;$launcherDir", "User")
    $env:Path = "$env:Path;$launcherDir"
    Write-Info "Adicionado $launcherDir ao PATH do usuário."
}

# ── Done ────────────────────────────────────────────────────────────────────
Write-Host ""
Write-OK "Estenio instalado com sucesso!"
Write-Host ""
Write-Host "Para começar, abra um NOVO terminal e execute:"
Write-Host "  estenio"
Write-Host ""
