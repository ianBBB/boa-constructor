@echo off
setlocal

:: ============================================================================
:: Script: bootstrap.bat
:: Purpose: Downloads and installs UV - An extremely fast Python package and project manager, written in Rust.
:: Usage: bootstrap.bat
:: ============================================================================

echo.
echo ========================================
echo UV Installer
echo ========================================
echo.

:: Check if PowerShell is available
where powershell >nul 2>&1
if errorlevel 1 (
    echo ERROR: PowerShell is not found on this system.
    echo Please ensure PowerShell is installed.
    echo Alternatively, follow the installation instructions for UV at
    echo https://docs.astral.sh/uv/getting-started/installation/
    pause
    exit /b 1
)

:: Execute the PowerShell command
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

:: Check if the command succeeded
if errorlevel 1 (
    echo.
    echo ERROR: The installation script failed with error code %errorlevel%.
    echo Alternatively, follow the installation instructions for UV at
    echo https://docs.astral.sh/uv/getting-started/installation/
    pause
    exit /b %errorlevel%
) else (
    echo.
    echo Installation completed successfully.
)

echo.
pause
endlocal
