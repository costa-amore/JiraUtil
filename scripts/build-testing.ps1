# Build Testing Functions
# This script contains functions for running tests during the build process

function Invoke-BuildTests {
    <#
    .SYNOPSIS
    Runs unit tests before building executables.
    
    .DESCRIPTION
    Executes unit tests using pytest and ensures all tests pass before proceeding with the build.
    This is a required step to ensure code quality before creating executables.
    
    .EXAMPLE
    Invoke-BuildTests
    
    .OUTPUTS
    Returns $true if all tests pass, $false otherwise.
    #>
    
    Write-Host "[TEST] Running unit tests..." -ForegroundColor Yellow
    Write-Host "All tests must pass before building executables" -ForegroundColor Cyan

    try {
        # Detect Python executable path (same logic as main build script)
        $PythonExe = "python"
        if (Test-Path ".\.venv\Scripts\python.exe") {
            $PythonExe = ".\.venv\Scripts\python.exe"
            Write-Host "[INFO] Using virtual environment Python for tests" -ForegroundColor Blue
        } else {
            Write-Host "[INFO] Using system Python for tests" -ForegroundColor Blue
        }
        
        # Use the documented test runner for consistent behavior
        # This ensures the same test environment as local development
        $process = Start-Process -FilePath "powershell" -ArgumentList "-ExecutionPolicy", "Bypass", "-File", "run.ps1", "tests/run_tests.py" -Wait -PassThru -NoNewWindow
        if ($process.ExitCode -ne 0) {
            Write-Host "[FAIL] Unit tests failed! Build aborted." -ForegroundColor Red
            Write-Host "Please fix all test failures before building executables." -ForegroundColor Red
            return $false
        }
        Write-Host "[OK] All unit tests passed! Proceeding with markdown linting..." -ForegroundColor Green
        return $true
    } catch {
        Write-Host "[FAIL] Failed to run unit tests: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "Please ensure the test environment is properly set up." -ForegroundColor Red
        return $false
    }
}

function Invoke-MarkdownLinting {
    <#
    .SYNOPSIS
    Runs markdown linting on source documentation.
    
    .DESCRIPTION
    Executes markdown linting to ensure documentation quality and consistency.
    
    .PARAMETER SourcePath
    Path to the source documentation directory.
    
    .PARAMETER ReadmePath
    Path to the main README file.
    
    .PARAMETER Fix
    Whether to automatically fix linting issues.
    
    .EXAMPLE
    Invoke-MarkdownLinting -SourcePath "docs/" -ReadmePath "README.md" -Fix
    #>
    
    param(
        [string]$SourcePath,
        [string]$ReadmePath,
        [switch]$Fix
    )
    
    Write-Host "[LINT] Running markdown linting on source documentation..." -ForegroundColor Yellow
    & "$PSScriptRoot\lint-markdown.ps1" -SourcePath $SourcePath -ReadmePath $ReadmePath -Fix
    return $LASTEXITCODE -eq 0
}
