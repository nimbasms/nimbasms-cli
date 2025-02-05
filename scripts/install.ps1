# Installation directory
$InstallDir = "$env:LocalAppData\NimbaSMS"
$BinaryName = "nimbasms.exe"

# Print banner
Write-Host "╔═══════════════════════════════════════╗"
Write-Host "║       Nimba SMS CLI Installer         ║"
Write-Host "╚═══════════════════════════════════════╝"

# Create installation directory
New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null

# Download binary
$BinaryUrl = "https://github.com/nimbasms/nimbasms-cli/releases/latest/download/nimbasms-windows-amd64.exe"
$BinaryPath = Join-Path $InstallDir $BinaryName

Write-Host "Downloading Nimba SMS CLI..." -ForegroundColor Yellow
try {
    Invoke-WebRequest -Uri $BinaryUrl -OutFile $BinaryPath
} catch {
    Write-Host "Failed to download CLI binary" -ForegroundColor Red
    exit 1
}

# Add to PATH if not already there
$CurrentPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($CurrentPath -notlike "*$InstallDir*") {
    [Environment]::SetEnvironmentVariable(
        "Path",
        "$CurrentPath;$InstallDir",
        "User"
    )
    $env:Path = "$env:Path;$InstallDir"
}

Write-Host "Nimba SMS CLI has been installed successfully!" -ForegroundColor Green
Write-Host "You can now use the 'nimbasms' command." -ForegroundColor Yellow
Write-Host "Try 'nimbasms --help' for usage information." -ForegroundColor Yellow