Param(
    [Parameter(Mandatory=$true, Position=0)]
    [string]$ScriptPath,

    [Parameter(ValueFromRemainingArguments=$true)]
    [string[]]$Args
)

$ErrorActionPreference = 'Stop'

$venvPython = Join-Path -Path $PSScriptRoot -ChildPath ".venv/Scripts/python.exe"
if (-not (Test-Path $venvPython)) {
    Write-Host "Creating virtual environment at .venv ..."
    & py -3 -m venv .venv
}

if (-not (Test-Path $venvPython)) {
    throw "Virtual environment was not created successfully. Ensure Python is installed and 'py' launcher is available."
}

if (-not (Test-Path $ScriptPath)) {
    throw "Script not found: $ScriptPath"
}

# Check if this is a test file (but not the test runner script)
if ($ScriptPath -match "test.*\.py$" -and $ScriptPath -notmatch "run_tests\.py$") {
    # Create a copy of arguments to avoid modifying the built-in $Args variable
    $scriptArgs = $Args.Clone()
    # If no traceback option specified, default to --tb=line for cleaner output
    if (-not ($scriptArgs -contains "--tb=short" -or $scriptArgs -contains "--tb=line" -or $scriptArgs -contains "--tb=no" -or $scriptArgs -contains "--tb=auto" -or $scriptArgs -contains "--tb=long")) {
        $scriptArgs += "--tb=line"
    }
    # Run with pytest for test files
    & $venvPython -m pytest $ScriptPath @scriptArgs
    $exitCode = $LASTEXITCODE
} else {
    # Run the target script with any extra args
    & $venvPython $ScriptPath @Args
    $exitCode = $LASTEXITCODE
}

# Exit with the same code as the Python process
exit $exitCode

