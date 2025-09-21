# Rebuild Virtual Environment Script
# This script rebuilds the .venv folder while preserving jira_config.env

param(
    [switch]$Force
)

$ErrorActionPreference = 'Stop'

Write-Host "🔄 Rebuilding virtual environment..." -ForegroundColor Cyan

# Check if .venv exists, if not run initial setup
if (-not (Test-Path .venv)) {
    Write-Host "ℹ️  No .venv folder found. Running initial setup..." -ForegroundColor Yellow
    
    # Create virtual environment
    Write-Host "🆕 Creating virtual environment..." -ForegroundColor Yellow
    py -3 -m venv .venv
    
    if (-not (Test-Path .venv\Scripts\python.exe)) {
        Write-Host "❌ Failed to create virtual environment. Ensure Python is installed." -ForegroundColor Red
        exit 1
    }
    
    # Install dependencies
    Write-Host "📦 Installing dependencies from requirements.txt..." -ForegroundColor Yellow
    .\.venv\Scripts\python.exe -m pip install -r requirements.txt
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to install dependencies." -ForegroundColor Red
        exit 1
    }
    
    # Copy example config if no config exists
    if (-not (Test-Path .venv\jira_config.env) -and (Test-Path .\jira_config_example.env)) {
        Copy-Item .\jira_config_example.env .venv\jira_config.env
        Write-Host "📋 Copied jira_config_example.env to .venv\jira_config.env" -ForegroundColor Green
        Write-Host "💡 Edit .venv\jira_config.env with your Jira credentials" -ForegroundColor Cyan
    }
    
    Write-Host "🎉 Initial setup completed!" -ForegroundColor Green
    Write-Host "💡 You can now run: ./run.ps1 .\JiraCsv.py --help" -ForegroundColor Cyan
    exit 0
}

# Backup jira_config.env if it exists
if (Test-Path .venv\jira_config.env) {
    Copy-Item .venv\jira_config.env .\jira_config_backup.env
    Write-Host "✅ Backed up jira_config.env to jira_config_backup.env" -ForegroundColor Green
} else {
    Write-Host "ℹ️  No jira_config.env found in .venv folder" -ForegroundColor Yellow
}

# Remove the old virtual environment
Write-Host "🗑️  Removing old virtual environment..." -ForegroundColor Yellow
Remove-Item -Recurse -Force .venv

# Recreate it
Write-Host "🆕 Creating new virtual environment..." -ForegroundColor Yellow
py -3 -m venv .venv

if (-not (Test-Path .venv\Scripts\python.exe)) {
    Write-Host "❌ Failed to create virtual environment. Ensure Python is installed." -ForegroundColor Red
    exit 1
}

# Install all dependencies
Write-Host "📦 Installing dependencies from requirements.txt..." -ForegroundColor Yellow
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install dependencies." -ForegroundColor Red
    exit 1
}

# Restore jira_config.env file
if (Test-Path .\jira_config_backup.env) {
    Copy-Item .\jira_config_backup.env .venv\jira_config.env
    Remove-Item .\jira_config_backup.env
    Write-Host "✅ Restored jira_config.env to .venv\jira_config.env" -ForegroundColor Green
}

Write-Host "🎉 Virtual environment rebuilt successfully!" -ForegroundColor Green
Write-Host "💡 You can now run: ./run.ps1 .\JiraCsv.py --help" -ForegroundColor Cyan
