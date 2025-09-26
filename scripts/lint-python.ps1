# Python Linting Script
# Runs Python linting on source code, tests, and tools

param(
    [Parameter(Mandatory=$false)]
    [string[]]$Directories = @("src/", "tests/", "tools/"),
    
    [Parameter(Mandatory=$false)]
    [string[]]$Files = @(),
    
    [Parameter(Mandatory=$false)]
    [switch]$Fix = $false
)

# Import color utilities
. "$PSScriptRoot\color_utils.ps1"

function Invoke-PythonLinting {
    param(
        [string[]]$Directories,
        [string[]]$Files,
        [bool]$IsFix = $false
    )
    
    Write-Host "[LINT] Running Python linting..." -ForegroundColor Yellow
    
    # Check if Python linter script exists
    if (-not (Test-Path "tools\python_linter.py")) {
        Write-Host "[ERROR] Python linter script not found: tools\python_linter.py" -ForegroundColor Red
        return $false
    }
    
    # Build command arguments
    $arguments = @()
    
    if ($IsFix) {
        $arguments += "--fix"
    }
    
    if ($Files.Count -gt 0) {
        $arguments += "--files"
        $arguments += $Files
    } else {
        $arguments += "--directories"
        $arguments += $Directories
    }
    
    # Run Python linter
    try {
        $result = & python tools\python_linter.py @arguments
        return $result -eq 0
    } catch {
        Write-Host "[ERROR] Failed to run Python linter: $_" -ForegroundColor Red
        return $false
    }
}

# Main execution
$allPassed = $true

# Run Python linting
if (-not (Invoke-PythonLinting -Directories $Directories -Files $Files -IsFix $Fix)) {
    $allPassed = $false
}

if (-not $allPassed) {
    exit 1
} else {
    Write-Host "[OK] All Python linting completed successfully!" -ForegroundColor Green
    exit 0
}
