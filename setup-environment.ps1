# Rebuild Virtual Environment Script
# This script rebuilds the .venv folder while preserving jira_config.env

param(
    [switch]$Force
)

$ErrorActionPreference = 'Stop'

Write-Host "[REBUILD] Rebuilding virtual environment..." -ForegroundColor Cyan

# Check if .venv exists, if not run initial setup
if (-not (Test-Path .venv)) {
    Write-Host "[INFO] No .venv folder found. Running initial setup..." -ForegroundColor Yellow
    
    # Create virtual environment
    Write-Host "[NEW] Creating virtual environment..." -ForegroundColor Yellow
    py -3 -m venv .venv
    
    if (-not (Test-Path .venv\Scripts\python.exe)) {
        Write-Host "[FAIL] Failed to create virtual environment. Ensure Python is installed." -ForegroundColor Red
        exit 1
    }
    
    # Install dependencies
    Write-Host "[PACKAGE] Installing dependencies from requirements.txt..." -ForegroundColor Yellow
    .\.venv\Scripts\python.exe -m pip install -r requirements.txt
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[FAIL] Failed to install dependencies." -ForegroundColor Red
        exit 1
    }
    
    # Copy example config if no config exists
    if (-not (Test-Path .venv\jira_config.env) -and (Test-Path .\jira_config_example.env)) {
        Copy-Item .\jira_config_example.env .venv\jira_config.env
        Write-Host "[CONFIG] Copied jira_config_example.env to .venv\jira_config.env" -ForegroundColor Green
        Write-Host "[TIP] Edit .venv\jira_config.env with your Jira credentials" -ForegroundColor Cyan
    }
    
    Write-Host "[SUCCESS] Initial setup completed!" -ForegroundColor Green
    Write-Host "[TIP] You can now run: ./run.ps1 .\JiraUtil.py --help" -ForegroundColor Cyan
    exit 0
}

# Backup jira_config.env if it exists
if (Test-Path .venv\jira_config.env) {
    Copy-Item .venv\jira_config.env .\jira_config_backup.env
    Write-Host "[OK] Backed up jira_config.env to jira_config_backup.env" -ForegroundColor Green
} else {
    Write-Host "[INFO] No jira_config.env found in .venv folder" -ForegroundColor Yellow
}

# Deactivate current virtual environment if active
if ($env:VIRTUAL_ENV) {
    Write-Host "[REBUILD] Deactivating current virtual environment..." -ForegroundColor Yellow
    # In PowerShell, we need to remove the virtual environment from the PATH
    $env:PATH = $env:PATH -replace [regex]::Escape($env:VIRTUAL_ENV + "\Scripts;"), ""
    $env:VIRTUAL_ENV = $null
    Write-Host "[OK] Virtual environment deactivated" -ForegroundColor Green
}

# Remove the old virtual environment
Write-Host "[CLEAN] Removing old virtual environment..." -ForegroundColor Yellow
# Kill any Python processes that might be using the virtual environment
taskkill /f /im python.exe 2>$null
Start-Sleep 2
Remove-Item -Recurse -Force .venv -ErrorAction SilentlyContinue

# Check if removal was successful
if (Test-Path .venv) {
    Write-Host "[FAIL] Failed to remove old virtual environment. Please close any Python processes and try again." -ForegroundColor Red
    Write-Host "[TIP] You can also manually delete the .venv folder and run this script again." -ForegroundColor Yellow
    exit 1
}

# Recreate it
Write-Host "[NEW] Creating new virtual environment..." -ForegroundColor Yellow
py -3 -m venv .venv

if (-not (Test-Path .venv\Scripts\python.exe)) {
    Write-Host "[FAIL] Failed to create virtual environment. Ensure Python is installed." -ForegroundColor Red
    exit 1
}

# Install all dependencies
Write-Host "[PACKAGE] Installing dependencies from requirements.txt..." -ForegroundColor Yellow
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

if ($LASTEXITCODE -ne 0) {
    Write-Host "[FAIL] Failed to install dependencies." -ForegroundColor Red
    exit 1
}

# Restore jira_config.env file
if (Test-Path .\jira_config_backup.env) {
    Copy-Item .\jira_config_backup.env .venv\jira_config.env
    Remove-Item .\jira_config_backup.env
    Write-Host "[OK] Restored jira_config.env to .venv\jira_config.env" -ForegroundColor Green
}

Write-Host "[SUCCESS] Virtual environment rebuilt successfully!" -ForegroundColor Green
Write-Host "[TIP] You can now run: ./run.ps1 .\JiraUtil.py --help" -ForegroundColor Cyan