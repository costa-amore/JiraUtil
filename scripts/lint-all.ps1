# Lint All Script
# Runs all linters (Python, PowerShell, Markdown) and optionally fixes issues

param(
    [Parameter(Mandatory=$false)]
    [switch]$Fix = $false,
    
    [Parameter(Mandatory=$false)]
    [switch]$Help = $false
)

if ($Help) {
    Write-Host "Lint All Script" -ForegroundColor Yellow
    Write-Host "===============" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Usage:" -ForegroundColor Cyan
    Write-Host "  .\scripts\lint-all.ps1           # Check for linting issues"
    Write-Host "  .\scripts\lint-all.ps1 -Fix      # Fix linting issues automatically"
    Write-Host "  .\scripts\lint-all.ps1 -Help     # Show this help"
    Write-Host ""
    Write-Host "This script runs:" -ForegroundColor Cyan
    Write-Host "  - Python linting (flake8, black, isort)"
    Write-Host "  - PowerShell linting (custom rules)"
    Write-Host "  - Markdown linting (formatting rules)"
    Write-Host ""
    Write-Host "Run this before building or releasing to ensure code quality." -ForegroundColor Green
    exit 0
}

# Import linter functions
. .\scripts\lint-python.ps1
. .\scripts\lint-powershell.ps1
. .\scripts\lint-markdown.ps1

Write-Host "Running all linters..." -ForegroundColor Yellow
if ($Fix) {
    Write-Host "Auto-fix mode enabled" -ForegroundColor Cyan
}

$allPassed = $true

# Run Python linting
Write-Host "`n[1/3] Python Linting..." -ForegroundColor Yellow
if (-not (Invoke-PythonLinting -Directories @("src/", "tests/", "tools/") -Fix:$Fix)) {
    $allPassed = $false
    Write-Host "[FAIL] Python linting failed" -ForegroundColor Red
} else {
    Write-Host "[OK] Python linting passed" -ForegroundColor Green
}

# Run PowerShell linting
Write-Host "`n[2/3] PowerShell Linting..." -ForegroundColor Yellow
if (-not (Invoke-PowerShellLinting -Directories @("scripts/") -Fix:$Fix)) {
    $allPassed = $false
    Write-Host "[FAIL] PowerShell linting failed" -ForegroundColor Red
} else {
    Write-Host "[OK] PowerShell linting passed" -ForegroundColor Green
}

# Run Markdown linting
Write-Host "`n[3/3] Markdown Linting..." -ForegroundColor Yellow
if (-not (Invoke-MarkdownLinting -SourcePath @("docs/", ".cursor/", "README.md") -Description "All markdown files" -IsFix:$Fix)) {
    $allPassed = $false
    Write-Host "[FAIL] Markdown linting failed" -ForegroundColor Red
} else {
    Write-Host "[OK] Markdown linting passed" -ForegroundColor Green
}

# Summary
Write-Host "`n" + "="*50 -ForegroundColor Gray
if ($allPassed) {
    Write-Host "All linters passed! ✓" -ForegroundColor Green
    if ($Fix) {
        Write-Host "Any auto-fixes have been applied." -ForegroundColor Cyan
    }
} else {
    Write-Host "Some linters failed! ✗" -ForegroundColor Red
    if ($Fix) {
        Write-Host "Some issues may have been auto-fixed. Please review and commit changes." -ForegroundColor Yellow
    } else {
        Write-Host "Run with -Fix to attempt automatic fixes." -ForegroundColor Yellow
    }
    exit 1
}
