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
    
    # Upgrade pip first to avoid warnings
    Write-Host "[PACKAGE] Upgrading pip to latest version..." -ForegroundColor Yellow
    .\.venv\Scripts\python.exe -m pip install --upgrade pip

    # Install dependencies
    Write-Host "[PACKAGE] Installing dependencies from requirements.txt..." -ForegroundColor Yellow
    .\.venv\Scripts\python.exe -m pip install -r requirements.txt
    
    # Install Windows-specific dependencies
    if (Test-Path "requirements-windows.txt") {
        Write-Host "[PACKAGE] Installing Windows-specific dependencies..." -ForegroundColor Yellow
        .\.venv\Scripts\python.exe -m pip install -r requirements-windows.txt
    }
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[FAIL] Failed to install dependencies." -ForegroundColor Red
        exit 1
    }
    
    # Store requirements hash for future change detection
    if (Test-Path "requirements.txt") {
        $requirementsHash = (Get-FileHash "requirements.txt" -Algorithm SHA256).Hash
        $requirementsHash | Out-File ".venv\requirements.hash" -Encoding UTF8
        Write-Host "[INFO] Stored requirements hash for change detection" -ForegroundColor Green
    }
    
    # Copy example config if no config exists
    if (-not (Test-Path .venv\jira_config.env) -and (Test-Path .\jira_config_example.env)) {
        Copy-Item .\jira_config_example.env .venv\jira_config.env
        Write-Host "[CONFIG] Copied jira_config_example.env to .venv\jira_config.env" -ForegroundColor Green
        Write-Host "[TIP] Edit .venv\jira_config.env with your Jira credentials" -ForegroundColor Cyan
    }
    
    Write-Host "[SUCCESS] Initial setup completed!" -ForegroundColor Green
    Write-Host "[TIP] You can now run: ./run.ps1 .\JiraUtil.py --help" -ForegroundColor Cyan
} else {
    Write-Host "[INFO] Virtual environment already exists. Checking for requirement changes..." -ForegroundColor Green
    
    # Check if requirements.txt has changed since last install
    $requirementsFile = "requirements.txt"
    $requirementsHashFile = ".venv\requirements.hash"
    
    if (Test-Path $requirementsFile) {
        $currentHash = (Get-FileHash $requirementsFile -Algorithm SHA256).Hash
        
        if (Test-Path $requirementsHashFile) {
            $storedHash = Get-Content $requirementsHashFile
            if ($currentHash -eq $storedHash) {
                Write-Host "[INFO] Requirements unchanged. Skipping dependency installation." -ForegroundColor Green
            } else {
                Write-Host "[INFO] Requirements have changed. Updating dependencies..." -ForegroundColor Yellow
                
                # Upgrade pip first
                Write-Host "[PACKAGE] Upgrading pip to latest version..." -ForegroundColor Yellow
                .\.venv\Scripts\python.exe -m pip install --upgrade pip
                
                # Install/update dependencies
                Write-Host "[PACKAGE] Installing/updating dependencies from requirements.txt..." -ForegroundColor Yellow
                .\.venv\Scripts\python.exe -m pip install -r requirements.txt
                
                # Install Windows-specific dependencies
                if (Test-Path "requirements-windows.txt") {
                    Write-Host "[PACKAGE] Installing Windows-specific dependencies..." -ForegroundColor Yellow
                    .\.venv\Scripts\python.exe -m pip install -r requirements-windows.txt
                }
                
                if ($LASTEXITCODE -ne 0) {
                    Write-Host "[FAIL] Failed to install dependencies." -ForegroundColor Red
                    exit 1
                }
                
                # Store the new hash
                $currentHash | Out-File $requirementsHashFile -Encoding UTF8
                Write-Host "[OK] Dependencies updated successfully!" -ForegroundColor Green
            }
        } else {
            Write-Host "[INFO] No requirements hash found. Installing dependencies..." -ForegroundColor Yellow
            
            # Upgrade pip first
            Write-Host "[PACKAGE] Upgrading pip to latest version..." -ForegroundColor Yellow
            .\.venv\Scripts\python.exe -m pip install --upgrade pip
            
            # Install dependencies
            Write-Host "[PACKAGE] Installing dependencies from requirements.txt..." -ForegroundColor Yellow
            .\.venv\Scripts\python.exe -m pip install -r requirements.txt
            
            # Install Windows-specific dependencies
            if (Test-Path "requirements-windows.txt") {
                Write-Host "[PACKAGE] Installing Windows-specific dependencies..." -ForegroundColor Yellow
                .\.venv\Scripts\python.exe -m pip install -r requirements-windows.txt
            }
            
            if ($LASTEXITCODE -ne 0) {
                Write-Host "[FAIL] Failed to install dependencies." -ForegroundColor Red
                exit 1
            }
            
            # Store the hash
            $currentHash | Out-File $requirementsHashFile -Encoding UTF8
            Write-Host "[OK] Dependencies installed successfully!" -ForegroundColor Green
        }
    } else {
        Write-Host "[WARN] requirements.txt not found. Skipping dependency management." -ForegroundColor Yellow
    }
    
    Write-Host "[TIP] Use -Force to rebuild the virtual environment" -ForegroundColor Cyan
}

# Only rebuild if Force is specified
if ($Force) {
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

# Upgrade pip first to avoid warnings
Write-Host "[PACKAGE] Upgrading pip to latest version..." -ForegroundColor Yellow
.\.venv\Scripts\python.exe -m pip install --upgrade pip

# Install all dependencies
Write-Host "[PACKAGE] Installing dependencies from requirements.txt..." -ForegroundColor Yellow
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

# Install Windows-specific dependencies
if (Test-Path "requirements-windows.txt") {
    Write-Host "[PACKAGE] Installing Windows-specific dependencies..." -ForegroundColor Yellow
    .\.venv\Scripts\python.exe -m pip install -r requirements-windows.txt
}

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
}

# Always activate the virtual environment
Write-Host ""
Write-Host "[ACTIVATION] Activating virtual environment..." -ForegroundColor Yellow

# Activate the virtual environment in the current PowerShell session
Write-Host "[INFO] Activating virtual environment for current session..." -ForegroundColor Cyan
& .\.venv\Scripts\Activate.ps1

Write-Host "[INFO] Virtual environment is now active!" -ForegroundColor Green
Write-Host "[INFO] Python path: $(Get-Command python).Source" -ForegroundColor Cyan
Write-Host ""
Write-Host "[TESTING] Running tests to verify setup..." -ForegroundColor Yellow
python tests/run_tests.py
if ($LASTEXITCODE -eq 0) {
    Write-Host "[SUCCESS] Tests passed! Setup is complete." -ForegroundColor Green
} else {
    Write-Host "[WARN] Some tests failed, but virtual environment is ready." -ForegroundColor Yellow
}
Write-Host ""
Write-Host "[USAGE] You can now run:" -ForegroundColor Cyan
Write-Host "  - Tests: python tests/run_tests.py" -ForegroundColor White
Write-Host "  - Main app: python .\JiraUtil.py --help" -ForegroundColor White
Write-Host "  - Or use run script: ./run.ps1 tests/run_tests.py" -ForegroundColor White
Write-Host ""
Write-Host "[NOTE] Virtual environment is now active in this PowerShell session!" -ForegroundColor Green
Write-Host "[NOTE] To activate in new sessions, run: .\.venv\Scripts\Activate.ps1" -ForegroundColor Cyan