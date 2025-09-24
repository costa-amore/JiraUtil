# Markdown Linting Script
# Runs markdown linting on source and generated documentation

param(
    [Parameter(Mandatory=$false)]
    [string]$SourcePath = "docs/",
    
    [Parameter(Mandatory=$false)]
    [string]$ReadmePath = "README.md",
    
    [Parameter(Mandatory=$false)]
    [string]$GeneratedPath = "",
    
    [Parameter(Mandatory=$false)]
    [string]$GeneratedReadmePath = "",
    
    [Parameter(Mandatory=$false)]
    [switch]$Fix = $false
)

# Import color utilities
. "$PSScriptRoot\color_utils.ps1"

function Invoke-MarkdownLinting {
    param(
        [string]$Path,
        [string]$Description,
        [bool]$IsFix = $false
    )
    
    Write-Host "[LINT] Running markdown linting on $Description..." -ForegroundColor Yellow
    
    try {
        if ($IsFix) {
            # First try to auto-fix issues
            Write-Host "[LINT] Attempting to auto-fix markdown issues..." -ForegroundColor Cyan
            $arguments = @("tools\markdown_linter.py", "--fix") + $Path.Split(' ')
        $fixProcess = Start-Process -FilePath "python" -ArgumentList $arguments -Wait -PassThru -NoNewWindow
            if ($fixProcess.ExitCode -eq 0) {
                Write-Host "[OK] Auto-fix completed successfully!" -ForegroundColor Green
            } else {
                Write-Host "[INFO] Auto-fix completed with some issues remaining" -ForegroundColor Yellow
            }
        }
        
        # Now run linting to check for remaining issues
        Write-Host "[LINT] Running markdown linting after auto-fix..." -ForegroundColor Cyan
        $arguments = @("tools\markdown_linter.py") + $Path.Split(' ')
        $lintProcess = Start-Process -FilePath "python" -ArgumentList $arguments -Wait -PassThru -NoNewWindow
        if ($lintProcess.ExitCode -ne 0) {
            Write-Host "[FAIL] Markdown linting failed! Build aborted." -ForegroundColor Red
            Write-Host "Please fix all remaining markdown linting errors before building executables." -ForegroundColor Red
            Write-Host "Run 'python tools\markdown_linter.py $Path' to see specific issues." -ForegroundColor Red
            return $false
        }
        Write-Host "[OK] $Description linting passed!" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "[FAIL] Markdown linting failed: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "Please ensure the markdown linter script is available: tools\markdown_linter.py" -ForegroundColor Red
        return $false
    }
}

# Main execution
$allPassed = $true

# Lint source documentation
if (-not (Invoke-MarkdownLinting -Path "$SourcePath $ReadmePath" -Description "Source documentation" -IsFix $Fix)) {
    $allPassed = $false
}

# Lint generated documentation if paths provided
if ($GeneratedPath -and $GeneratedReadmePath) {
    if (-not (Invoke-MarkdownLinting -Path "$GeneratedPath $GeneratedReadmePath" -Description "Generated documentation" -IsFix $Fix)) {
        $allPassed = $false
    }
}

if (-not $allPassed) {
    exit 1
} else {
    Write-Host "[OK] All markdown linting completed successfully!" -ForegroundColor Green
    exit 0
}
