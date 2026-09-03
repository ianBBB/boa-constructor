[CmdletBinding()]
param(
    [string]$PythonExe = "python",
    [switch]$SkipCheck
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Push-Location $PSScriptRoot
try {
    if (-not (Get-Command $PythonExe -ErrorAction SilentlyContinue)) {
        throw "Python executable/command not found: $PythonExe"
    }

    if (-not (Test-Path -Path "dist")) {
        throw "dist/ does not exist. Run .\\release.ps1 first."
    }

    $artifacts = Get-ChildItem -Path "dist" -File -ErrorAction SilentlyContinue
    if (-not $artifacts) {
        throw "No artifacts found in dist/. Run .\\release.ps1 first."
    }

    if (-not $SkipCheck) {
        Write-Host "Running twine check before upload..."
        & $PythonExe -m twine check dist/*
    }

    Write-Host "Uploading artifacts to TestPyPI..."
    & $PythonExe -m twine upload --repository testpypi dist/*
}
finally {
    Pop-Location
}
