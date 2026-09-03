@echo off
setlocal

:: ============================================================================
:: Script: run.bat
:: Purpose: Launches Boa.
:: Usage: run.bat
:: ============================================================================

echo.
echo ========================================
echo Launching Boa
echo ========================================
echo.

:: Launch Boa
uv run Boa.py

:: Check if the command succeeded
if errorlevel 1 (
    echo.
    echo ERROR: Launching Boa failed with error code %errorlevel%.
    pause
    exit /b %errorlevel%
) else (
    echo.
    echo Thanks for using Boa.
)

echo.
pause
endlocal
