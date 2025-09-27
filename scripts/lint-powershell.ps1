#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Run PowerShell linter and fix issues.
#>

Write-Host "Running PowerShell linter..." -ForegroundColor Yellow

& .\run.ps1 tools\powershell_linter.py --fix --directories "scripts/"

if ($LASTEXITCODE -eq 0) {
    Write-Host "PowerShell linting passed" -ForegroundColor Green
    exit 0
} else {
    Write-Host "PowerShell linting failed" -ForegroundColor Red
    exit 1
}