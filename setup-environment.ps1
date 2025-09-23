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
Write-Host "[INFO] Checking for running Python processes..." -ForegroundColor Yellow
$pythonProcesses = Get-Process python -ErrorAction SilentlyContinue
if ($pythonProcesses) {
    Write-Host "[INFO] Found $($pythonProcesses.Count) Python process(es), terminating..." -ForegroundColor Yellow
    taskkill /f /im python.exe 2>$null
    Start-Sleep 3
} else {
    Write-Host "[INFO] No Python processes found" -ForegroundColor Green
}

# Try multiple removal strategies
Write-Host "[INFO] Attempting to remove .venv folder..." -ForegroundColor Yellow

# Strategy 1: Standard removal
try {
    Remove-Item -Recurse -Force .venv -ErrorAction Stop
    Write-Host "[OK] Successfully removed .venv folder" -ForegroundColor Green
} catch {
    Write-Host "[WARN] Standard removal failed: $($_.Exception.Message)" -ForegroundColor Yellow
    
    # Strategy 2: Use robocopy to empty the folder first
    Write-Host "[INFO] Trying alternative removal method..." -ForegroundColor Yellow
    try {
        # Create empty temp folder
        $tempFolder = "temp_empty_$(Get-Random)"
        New-Item -ItemType Directory -Path $tempFolder -Force | Out-Null
        
        # Use robocopy to mirror empty folder (effectively deleting contents)
        robocopy $tempFolder .venv /MIR /NFL /NDL /NJH /NJS /NC /NS /NP /Q 2>$null
        
        # Remove temp folder
        Remove-Item -Recurse -Force $tempFolder -ErrorAction SilentlyContinue
        
        # Now try to remove .venv again
        Remove-Item -Recurse -Force .venv -ErrorAction Stop
        Write-Host "[OK] Successfully removed .venv folder using alternative method" -ForegroundColor Green
    } catch {
        Write-Host "[FAIL] All removal methods failed: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "[TIP] Possible causes:" -ForegroundColor Yellow
        Write-Host "  - Antivirus software is scanning the folder" -ForegroundColor Yellow
        Write-Host "  - File handles are still open (try restarting your terminal)" -ForegroundColor Yellow
        Write-Host "  - Permission issues (run as administrator)" -ForegroundColor Yellow
        Write-Host "  - Windows file system delays (wait a few minutes and try again)" -ForegroundColor Yellow
        Write-Host "[TIP] You can also manually delete the .venv folder and run this script again" -ForegroundColor Yellow
        exit 1
    }
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