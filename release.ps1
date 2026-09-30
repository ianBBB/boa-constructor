[CmdletBinding()]
param(
    [string]$PythonExe = "python",
    [switch]$NoClean,
    [switch]$NoCheck
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if (-not (Get-Command $PythonExe -ErrorAction SilentlyContinue)) {
    throw "Python executable/command not found: $PythonExe"
}

Push-Location $PSScriptRoot
try {
    if (-not $NoClean) {
        Write-Host "Cleaning previous artifacts..."
        if (Test-Path -Path "dist") {
            Remove-Item -Recurse -Force "dist"
        }
        if (Test-Path -Path "build") {
            Remove-Item -Recurse -Force "build"
        }
        Get-ChildItem -Path . -Filter "*.egg-info" -Directory -ErrorAction SilentlyContinue |
            ForEach-Object { Remove-Item -Recurse -Force $_.FullName }
    }

    Write-Host "Building source distribution..."
    & $PythonExe -m build --no-isolation

    Write-Host "Building wheel distribution..."
    & $PythonExe -m build --wheel --no-isolation

    if (-not $NoCheck) {
        Write-Host "Running twine checks..."
        & $PythonExe -m twine check dist/*
    }

    Write-Host "Release artifacts are ready in dist/."
}
finally {
    Pop-Location
}
