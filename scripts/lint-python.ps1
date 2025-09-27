#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Run Python linter and fix issues.
#>

Write-Host "Running Python linter..." -ForegroundColor Yellow

& .\run.ps1 tools\python_linter.py --fix --directories "src/" "tests/" "tools/"

if ($LASTEXITCODE -eq 0) {
    Write-Host "Python linting passed" -ForegroundColor Green
    exit 0
} else {
    Write-Host "Python linting failed" -ForegroundColor Red
    exit 1
}