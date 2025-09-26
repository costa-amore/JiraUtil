# PowerShell Linting Script
# Runs PowerShell linting on scripts directory

param(
    [Parameter(Mandatory=$false)]
    [string[]]$Directories = @("scripts/"),
    
    [Parameter(Mandatory=$false)]
    [string[]]$Files = @(),
    
    [Parameter(Mandatory=$false)]
    [switch]$Fix = $false
)

# Import color utilities
. "$PSScriptRoot\color_utils.ps1"

function Invoke-PowerShellLinting {
    param(
        [string[]]$Directories,
        [string[]]$Files,
        [bool]$IsFix = $false
    )
    
    Write-Host "[LINT] Running PowerShell linting..." -ForegroundColor Yellow
    
    # Check if PowerShell linter script exists
    if (-not (Test-Path "tools\powershell_linter.py")) {
        Write-Host "[ERROR] PowerShell linter script not found: tools\powershell_linter.py" -ForegroundColor Red
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
    
    # Run PowerShell linter
    try {
        $result = & .\run.ps1 tools\powershell_linter.py @arguments
        return $result -eq 0
    } catch {
        Write-Host "[ERROR] Failed to run PowerShell linter: $_" -ForegroundColor Red
        return $false
    }
}

# Main execution
$allPassed = $true

# Run PowerShell linting
if (-not (Invoke-PowerShellLinting -Directories $Directories -Files $Files -IsFix $Fix)) {
    $allPassed = $false
}

if (-not $allPassed) {
    exit 1
} else {
    Write-Host "[OK] All PowerShell linting completed successfully!" -ForegroundColor Green
    exit 0
}
