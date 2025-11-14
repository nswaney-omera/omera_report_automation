# Check Prerequisites for Building NSIS Installer
# Run this script first to verify your system is ready

$ErrorActionPreference = "Continue"

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Prerequisites Check" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

$allGood = $true

# Check 1: Python
Write-Host "[1/5] Checking Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    $pythonPath = (Get-Command python).Source
    Write-Host "  ✓ Python installed: $pythonVersion" -ForegroundColor Green
    Write-Host "    Location: $pythonPath" -ForegroundColor Gray

    # Check Python version (should be 3.10+)
    $versionMatch = $pythonVersion -match "Python (\d+)\.(\d+)"
    if ($versionMatch) {
        $major = [int]$matches[1]
        $minor = [int]$matches[2]
        if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 10)) {
            Write-Host "  ⚠ Warning: Python 3.10+ recommended (you have $major.$minor)" -ForegroundColor Yellow
        }
    }
} catch {
    Write-Host "  ✗ Python NOT found" -ForegroundColor Red
    Write-Host "    Install from: https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host "    Make sure to check 'Add Python to PATH' during installation" -ForegroundColor Yellow
    $allGood = $false
}
Write-Host ""

# Check 2: pip
Write-Host "[2/5] Checking pip..." -ForegroundColor Yellow
try {
    $pipVersion = python -m pip --version 2>&1
    Write-Host "  ✓ pip installed: $pipVersion" -ForegroundColor Green
} catch {
    Write-Host "  ✗ pip NOT found" -ForegroundColor Red
    Write-Host "    Install with: python -m ensurepip --upgrade" -ForegroundColor Yellow
    $allGood = $false
}
Write-Host ""

# Check 3: NSIS
Write-Host "[3/5] Checking NSIS..." -ForegroundColor Yellow
$nsisPath = "C:\Program Files (x86)\NSIS\makensis.exe"
if (Test-Path $nsisPath) {
    try {
        $nsisVersion = & $nsisPath /VERSION
        Write-Host "  ✓ NSIS installed: v$nsisVersion" -ForegroundColor Green
        Write-Host "    Location: $nsisPath" -ForegroundColor Gray
    } catch {
        Write-Host "  ⚠ NSIS found but cannot read version" -ForegroundColor Yellow
        Write-Host "    Location: $nsisPath" -ForegroundColor Gray
    }
} else {
    Write-Host "  ✗ NSIS NOT found" -ForegroundColor Red
    Write-Host "    Download from: https://nsis.sourceforge.io/Download" -ForegroundColor Yellow
    Write-Host "    Install to default location: C:\Program Files (x86)\NSIS\" -ForegroundColor Yellow
    $allGood = $false
}
Write-Host ""

# Check 4: PyInstaller
Write-Host "[4/5] Checking PyInstaller..." -ForegroundColor Yellow
try {
    $pyinstallerVersion = python -m PyInstaller --version 2>&1
    Write-Host "  ✓ PyInstaller installed: $pyinstallerVersion" -ForegroundColor Green
} catch {
    Write-Host "  ✗ PyInstaller NOT found" -ForegroundColor Red
    Write-Host "    Install with: python -m pip install pyinstaller" -ForegroundColor Yellow
    $allGood = $false
}
Write-Host ""

# Check 5: tomlkit
Write-Host "[5/5] Checking tomlkit..." -ForegroundColor Yellow
try {
    python -c "import tomlkit" 2>&1 | Out-Null
    Write-Host "  ✓ tomlkit installed" -ForegroundColor Green
} catch {
    Write-Host "  ✗ tomlkit NOT found" -ForegroundColor Red
    Write-Host "    Install with: python -m pip install tomlkit" -ForegroundColor Yellow
    $allGood = $false
}
Write-Host ""

# Summary
Write-Host "=========================================" -ForegroundColor Cyan
if ($allGood) {
    Write-Host "ALL PREREQUISITES MET ✓" -ForegroundColor Green
    Write-Host "=========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "You're ready to build the installer!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "  1. Run build_installer.bat (double-click)" -ForegroundColor White
    Write-Host "  OR" -ForegroundColor Gray
    Write-Host "  2. Run: powershell -ExecutionPolicy Bypass -File build_installer.ps1" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host "MISSING PREREQUISITES ✗" -ForegroundColor Red
    Write-Host "=========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Please install the missing components above." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Quick install commands:" -ForegroundColor Yellow
    Write-Host "  python -m pip install pyinstaller tomlkit" -ForegroundColor White
    Write-Host ""
    Write-Host "Then run this script again to verify." -ForegroundColor Yellow
    Write-Host ""
}

# Optional: Check project files
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Project Files Check" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

$projectFiles = @{
    "exec_reports/server.py" = "MCP server entry point"
    "exec_reports/pyproject.toml" = "Version and dependencies"
    "exec_reports/installer.nsi" = "NSIS configuration"
    "exec_reports/file_version_info.txt" = "Windows metadata"
    "installer/common-mcp-install.nsh" = "NSIS template"
    "installer/add-mcp-server.ps1" = "Claude config script"
}

foreach ($file in $projectFiles.Keys) {
    if (Test-Path $file) {
        Write-Host "  ✓ $file" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $file - MISSING!" -ForegroundColor Red
        Write-Host "    Description: $($projectFiles[$file])" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
