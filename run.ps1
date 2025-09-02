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

# Run the target script with any extra args
& $venvPython $ScriptPath @Args

