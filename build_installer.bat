@echo off
REM Simple wrapper to run the PowerShell build script
REM Double-click this file or run from command prompt

echo.
echo ========================================
echo Executive Reports MCP - Build Installer
echo ========================================
echo.

REM Check if PowerShell is available
where powershell >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: PowerShell not found!
    echo Please install PowerShell or run the build_installer.ps1 script directly.
    pause
    exit /b 1
)

REM Run the PowerShell script
powershell -ExecutionPolicy Bypass -File "%~dp0build_installer.ps1"

REM Check result
if %errorlevel% equ 0 (
    echo.
    echo Build completed successfully!
) else (
    echo.
    echo Build failed! Check the errors above.
)

echo.
pause
