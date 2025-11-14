# Build Windows Installer for Executive Reports MCP
# This script builds the NSIS installer locally without GitHub Actions
# Run with: .\build_installer.ps1

param(
    [switch]$SkipClean = $false
)

$ErrorActionPreference = "Stop"

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Executive Reports MCP - Local Build" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Store original location
$OriginalLocation = Get-Location

try {
    # Navigate to installer_v4 directory
    $ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
    Set-Location $ScriptDir

    Write-Host "[1/9] Checking prerequisites..." -ForegroundColor Yellow

    # Check Python
    try {
        $pythonVersion = python --version 2>&1
        Write-Host "  [OK] Python found: $pythonVersion" -ForegroundColor Green
    }
    catch {
        Write-Host "  [ERROR] Python not found! Please install Python 3.10+" -ForegroundColor Red
        throw "Python not found"
    }

    # Check NSIS
    $nsisPath = "C:\Program Files (x86)\NSIS\makensis.exe"
    if (-not (Test-Path $nsisPath)) {
        Write-Host "  [ERROR] NSIS not found at: $nsisPath" -ForegroundColor Red
        Write-Host "    Download from: https://nsis.sourceforge.io/Download" -ForegroundColor Yellow
        throw "NSIS not found"
    }
    $nsisVersion = & $nsisPath /VERSION
    Write-Host "  [OK] NSIS found: v$nsisVersion" -ForegroundColor Green

    # Check PyInstaller
    try {
        $pyinstallerVersion = python -m PyInstaller --version 2>&1
        Write-Host "  [OK] PyInstaller found: $pyinstallerVersion" -ForegroundColor Green
    }
    catch {
        Write-Host "  [WARN] PyInstaller not found, installing..." -ForegroundColor Yellow
        python -m pip install pyinstaller
        Write-Host "  [OK] PyInstaller installed" -ForegroundColor Green
    }

    # Check tomlkit
    try {
        python -c "import tomlkit" 2>&1 | Out-Null
        Write-Host "  [OK] tomlkit found" -ForegroundColor Green
    }
    catch {
        Write-Host "  [WARN] tomlkit not found, installing..." -ForegroundColor Yellow
        python -m pip install tomlkit
        Write-Host "  [OK] tomlkit installed" -ForegroundColor Green
    }

    Write-Host ""
    Write-Host "[2/9] Reading package version..." -ForegroundColor Yellow

    # Navigate to package directory
    Set-Location "exec_reports"

    # Get version and name from pyproject.toml
    $version = python -c "import tomlkit; print(tomlkit.parse(open('pyproject.toml').read())['project']['version'])"
    $name = python -c "import tomlkit; print(tomlkit.parse(open('pyproject.toml').read())['project']['name'])"

    Write-Host "  Package: $name" -ForegroundColor Cyan
    Write-Host "  Version: $version" -ForegroundColor Cyan
    Write-Host ""

    Write-Host "[3/9] Installing Python dependencies..." -ForegroundColor Yellow

    # Check if requirements.txt exists in parent directories
    if (Test-Path "../../requirements.txt") {
        Write-Host "  Installing from ../../requirements.txt..." -ForegroundColor Gray
        python -m pip install -r ../../requirements.txt -q
    }
    elseif (Test-Path "../requirements.txt") {
        Write-Host "  Installing from ../requirements.txt..." -ForegroundColor Gray
        python -m pip install -r ../requirements.txt -q
    }
    else {
        Write-Host "  [WARN] No requirements.txt found, skipping..." -ForegroundColor Yellow
    }

    # Install PyInstaller if not already installed
    python -m pip install pyinstaller --quiet
    Write-Host "  [OK] Dependencies ready" -ForegroundColor Green
    Write-Host ""

    Write-Host "[4/9] Cleaning old build artifacts..." -ForegroundColor Yellow

    if (-not $SkipClean) {
        if (Test-Path "build") {
            Remove-Item -Recurse -Force "build"
            Write-Host "  [OK] Removed build/" -ForegroundColor Gray
        }
        if (Test-Path "dist") {
            Remove-Item -Recurse -Force "dist"
            Write-Host "  [OK] Removed dist/" -ForegroundColor Gray
        }
        if (Test-Path "*.spec") {
            Remove-Item -Force "*.spec"
            Write-Host "  [OK] Removed *.spec files" -ForegroundColor Gray
        }
        Write-Host "  [OK] Clean complete" -ForegroundColor Green
    }
    else {
        Write-Host "  [SKIP] Skipped cleaning" -ForegroundColor Gray
    }
    Write-Host ""

    Write-Host "[5/9] Building executable with PyInstaller..." -ForegroundColor Yellow

    # Build PyInstaller command
    Write-Host "  Running pyinstaller..." -ForegroundColor Gray

    # Check if file_version_info.txt exists
    $versionFileArg = ""
    if (Test-Path "file_version_info.txt") {
        $versionFileArg = "--version-file=file_version_info.txt"
        Write-Host "  [OK] Using version info file" -ForegroundColor Gray
    }

    # Run PyInstaller
    $pyinstallerArgs = @(
        $versionFileArg
        "--add-data"
        "templates;templates"
        "--add-data"
        "utils;utils"
        "--add-data"
        "data;data"
        "--hidden-import=fastmcp"
        "--hidden-import=pydantic"
        "--hidden-import=pydantic_core"
        "--hidden-import=pydantic_settings"
        "--hidden-import=docx"
        "--hidden-import=lxml"
        "--hidden-import=lxml.etree"
        "--hidden-import=PIL"
        "--hidden-import=PIL.Image"
        "--hidden-import=starlette"
        "--hidden-import=uvicorn"
        "--hidden-import=httpx"
        "--hidden-import=click"
        "--hidden-import=rich"
        "--hidden-import=yaml"
        "--copy-metadata=fastmcp"
        "--copy-metadata=pydantic"
        "--copy-metadata=pydantic_core"
        "server.py"
        "--noconfirm"
    )

    # Filter out empty strings
    $pyinstallerArgs = $pyinstallerArgs | Where-Object { $_ -ne "" }

    & python -m PyInstaller $pyinstallerArgs

    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller failed with exit code $LASTEXITCODE"
    }

    # Verify output
    if (-not (Test-Path "dist/server")) {
        throw "PyInstaller output not found at dist/server/"
    }

    Write-Host "  [OK] Executable built successfully" -ForegroundColor Green
    Write-Host "  Location: dist/server/" -ForegroundColor Gray
    Write-Host ""

    Write-Host "[6/9] Creating .env file..." -ForegroundColor Yellow

    # Create .env file
    $envContent = @"
# Executive Reports MCP Server Configuration
# Add environment variables as needed
"@

    $envContent | Out-File -FilePath ".env" -Encoding utf8 -NoNewline
    Write-Host "  [OK] .env file created" -ForegroundColor Green
    Write-Host ""

    Write-Host "[7/9] Building NSIS installer..." -ForegroundColor Yellow

    # Verify installer.nsi exists
    if (-not (Test-Path "installer.nsi")) {
        throw "installer.nsi not found!"
    }

    # Run NSIS
    Write-Host "  Running makensis.exe..." -ForegroundColor Gray
    & $nsisPath /DVERSION="$version" "installer.nsi"

    if ($LASTEXITCODE -ne 0) {
        throw "NSIS build failed with exit code $LASTEXITCODE"
    }

    Write-Host "  [OK] NSIS installer created" -ForegroundColor Green
    Write-Host ""

    Write-Host "[8/9] Renaming installer..." -ForegroundColor Yellow

    # Find and rename the installer
    $installers = Get-ChildItem -Filter "*.exe" -File | Where-Object { $_.Name -notlike "*uninstall*" }

    if ($installers.Count -eq 0) {
        throw "No installer found!"
    }

    foreach ($installer in $installers) {
        $newName = "${name}-installer-v${version}.exe"

        # Remove existing file if it exists
        if (Test-Path $newName) {
            Remove-Item $newName -Force
        }

        Rename-Item -Path $installer.FullName -NewName $newName
        Write-Host "  [OK] Renamed: $($installer.Name) -> $newName" -ForegroundColor Green

        # Show file info
        $fileSize = (Get-Item $newName).Length / 1MB
        Write-Host "  Size: $([math]::Round($fileSize, 2)) MB" -ForegroundColor Gray
        Write-Host "  Location: $(Get-Location)\$newName" -ForegroundColor Gray
    }

    Write-Host ""
    Write-Host "[9/9] Build complete!" -ForegroundColor Green
    Write-Host ""
    Write-Host "=====================================" -ForegroundColor Cyan
    Write-Host "BUILD SUCCESSFUL" -ForegroundColor Green
    Write-Host "=====================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Installer created:" -ForegroundColor White
    Write-Host "  ${name}-installer-v${version}.exe" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "  1. Test the installer on a clean Windows VM" -ForegroundColor White
    Write-Host "  2. Verify it installs without Python" -ForegroundColor White
    Write-Host "  3. Check Claude Desktop integration works" -ForegroundColor White
    Write-Host "  4. Test the MCP server functionality" -ForegroundColor White
    Write-Host ""

}
catch {
    Write-Host ""
    Write-Host "=====================================" -ForegroundColor Red
    Write-Host "BUILD FAILED" -ForegroundColor Red
    Write-Host "=====================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Error: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Stack Trace:" -ForegroundColor Gray
    Write-Host $_.ScriptStackTrace -ForegroundColor Gray
    Write-Host ""
    exit 1
}
finally {
    # Return to original location
    Set-Location $OriginalLocation
}
