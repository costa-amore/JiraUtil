#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Run markdown linter and fix issues.
#>

Write-Host "Running markdown linter..." -ForegroundColor Yellow

& .\run.ps1 tools\markdown_linter.py --fix "docs/" ".cursor/" "README.md"

if ($LASTEXITCODE -eq 0) {
    Write-Host "Markdown linting passed" -ForegroundColor Green
    exit 0
} else {
    Write-Host "Markdown linting failed" -ForegroundColor Red
    exit 1
}