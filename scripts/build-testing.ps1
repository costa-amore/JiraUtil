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
        # Use the documented test runner for consistent behavior
        # This ensures the same test environment as local development
        # run.ps1 handles Python detection and virtual environment setup
        Write-Host "Running tests (output will stream in real-time):" -ForegroundColor Yellow
        
        # Run tests using run.ps1 to ensure proper virtual environment
        Write-Host ""
        $process = Start-Process -FilePath "cmd" -ArgumentList "/c", "powershell -ExecutionPolicy Bypass -File run.ps1 tests/run_tests.py all" -Wait -PassThru -NoNewWindow
        $testExitCode = $process.ExitCode
        
        if ($testExitCode -ne 0) {
            Write-Host "[FAIL] Unit tests failed! Build aborted." -ForegroundColor Red
            Write-Host "Please fix all test failures before building executables." -ForegroundColor Red
            Write-Host "Test exit code: $testExitCode" -ForegroundColor Red
            return $false
        }
        Write-Host "[OK] All unit tests passed!" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "[FAIL] Failed to run unit tests: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "Please ensure the test environment is properly set up." -ForegroundColor Red
        return $false
    }
}

# Run tests when script is executed directly
if ($MyInvocation.InvocationName -ne '.') {
    Invoke-BuildTests
}
