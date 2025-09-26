# Generic Build Executables Script
# This script compiles the JiraUtil project into standalone executables
# Use platform-specific convenience scripts for common use cases:
#   - build-windows.ps1 (Windows only)

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("windows")]
    [string]$Platform = "windows",  # Target platform: "windows" (only Windows currently supported, default)
    [switch]$Clean = $false,    # Clean build directories before building
    [switch]$BuildForRelease = $false  # Build for release (increment build number)
)

$ErrorActionPreference = 'Stop'

# Import build helper modules
. "$PSScriptRoot\build-testing.ps1"
. "$PSScriptRoot\build-versioning.ps1"
. "$PSScriptRoot\build-documentation.ps1"
. "$PSScriptRoot\build-packaging.ps1"
. "$PSScriptRoot\lint-python.ps1"
. "$PSScriptRoot\lint-powershell.ps1"

Write-Host "[BUILD] Building JiraUtil Executables" -ForegroundColor Cyan
Write-Host "Platform: $Platform" -ForegroundColor Yellow

# Run unit tests FIRST - REQUIRED before any version changes
if (-not (Invoke-BuildTests)) {
    exit 1
}

# Run all linters and check if any changes were made
Write-Host "[LINT] Running all linters..." -ForegroundColor Yellow

$linterChanges = $false

# Run markdown linting on all markdown files
if (-not (Invoke-MarkdownLinting -Fix)) {
    exit 1
}

# Run Python linting on all Python files
if (-not (Invoke-PythonLinting -Fix)) {
    exit 1
}

# Run PowerShell linting on all PowerShell files
if (-not (Invoke-PowerShellLinting -Fix)) {
    exit 1
}

# Check if any linters made changes
$gitStatus = git status --porcelain
if ($gitStatus) {
    Write-Host "[LINT] Linters made changes to files. Please review and commit them before building." -ForegroundColor Yellow
    Write-Host "Modified files:" -ForegroundColor Cyan
    Write-Host $gitStatus -ForegroundColor Gray
    Write-Host "Run 'git add .' and 'git commit -m \"fix: apply linter auto-fixes\"' to commit the changes." -ForegroundColor Green
    Write-Host "Then run the build again." -ForegroundColor Green
    exit 1
}


# Handle versioning AFTER tests pass
$IsCI = $env:CI -eq "true" -or $env:GITHUB_ACTIONS -eq "true"
$IsRelease = $BuildForRelease -eq $true

$version = Invoke-VersionManagement -IsRelease $IsRelease -IsCI $IsCI
New-VersionInfoFile

# Generate PyInstaller spec file
Write-Host "[SPEC] Generating PyInstaller spec file..." -ForegroundColor Yellow
python tools\generate-spec.py

# Detect Python executable path
$PythonExe = "python"
if (Test-Path ".\.venv\Scripts\python.exe") {
    $PythonExe = ".\.venv\Scripts\python.exe"
    Write-Host "[INFO] Using virtual environment Python" -ForegroundColor Blue
} else {
    Write-Host "[INFO] Using system Python" -ForegroundColor Blue
}

# Check if PyInstaller is installed
Write-Host "[PACKAGE] Checking PyInstaller installation..." -ForegroundColor Yellow
try {
    $PyInstallerVersion = & $PythonExe -m PyInstaller --version 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller not found"
    }
    Write-Host "[OK] PyInstaller version: $PyInstallerVersion" -ForegroundColor Green
} catch {
    Write-Host "[FAIL] PyInstaller not found. Installing..." -ForegroundColor Red
    & $PythonExe -m pip install pyinstaller
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[FAIL] Failed to install PyInstaller" -ForegroundColor Red
        exit 1
    }
    Write-Host "[OK] PyInstaller installed successfully" -ForegroundColor Green
}

# Clean build directories if requested
if ($Clean) {
    Write-Host "[CLEAN] Cleaning build directories..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force "dist", "build" -ErrorAction SilentlyContinue
    # Don't remove .spec files as they're needed for building
}

# Create build directory structure
$script:BuildDir = "build-executables"
if (Test-Path $BuildDir) {
    Remove-Item -Recurse -Force $BuildDir
}
New-Item -ItemType Directory -Path $BuildDir | Out-Null

# Function to create Windows launcher script
function New-WindowsLauncher {
    param(
        [string]$OutputDir,
        [string]$ExecutableName = "JiraUtil"
    )
    
    $LauncherContent = @"
@echo off
echo JiraUtil - Jira Administration Tool
echo ===================================
echo.
echo Edit jira_config.env with your Jira credentials, then run the tool.
echo.
pause
$ExecutableName.exe %*
"@
    $LauncherContent | Out-File -FilePath "$OutputDir\run.bat" -Encoding ASCII
}

# Function to get Windows executable path
function Get-WindowsExecutablePath {
    param(
        [string]$OutputDir,
        [string]$ExecutableName = "JiraUtil"
    )
    return "$OutputDir\$ExecutableName.exe"
}


# Function to build for a specific platform
function Build-Executable {
    param(
        [string]$PlatformName,
        [string]$TargetOS,
        [string]$IconPath = $null
    )
    
    Write-Host "`n[BUILD] Building for $PlatformName..." -ForegroundColor Cyan
    
    $OutputDir = "$script:BuildDir\$PlatformName"
    New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
    
    # Use the spec file for more control with virtual environment
    $PyInstallerCmd = @(
        ".\.venv\Scripts\python.exe", "-m", "PyInstaller"
        "JiraUtil.spec"
        "--distpath", $OutputDir       # Override output directory
        "--workpath", "build"          # Temporary build directory
        "--noconfirm"                  # Don't ask for confirmation
    )
    
    # Execute PyInstaller
    Write-Host "Running: $($PyInstallerCmd -join ' ')" -ForegroundColor Gray
    & $PyInstallerCmd[0] $PyInstallerCmd[1..($PyInstallerCmd.Length-1)]
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] $PlatformName build completed successfully" -ForegroundColor Green
        
               # Copy additional files
               Copy-Item "jira_config_example.env" "$OutputDir\jira_config.env" -ErrorAction SilentlyContinue
               
               # Create documentation structure
               New-DocumentationStructure -OutputDir $OutputDir -Version $version
        
        # Create Windows launcher script
        New-WindowsLauncher -OutputDir $OutputDir -ExecutableName "JiraUtil"
        
        # Get executable size
        $ExePath = Get-WindowsExecutablePath -OutputDir $OutputDir -ExecutableName "JiraUtil"
        if (Test-Path $ExePath) {
            $Size = (Get-Item $ExePath).Length
            $SizeMB = [math]::Round($Size / 1MB, 2)
            Write-Host "[PACKAGE] Executable size: $SizeMB MB" -ForegroundColor Cyan
        }
        
    } else {
        Write-Host "[FAIL] $PlatformName build failed" -ForegroundColor Red
        return $false
    }
    
    return $true
}

# Build for requested platforms
$BuildResults = @{}

if ($Platform -eq "windows") {
    $BuildResults["Windows"] = Build-Executable -PlatformName "Windows" -TargetOS "windows"
}


# Show build summary
Show-BuildSummary -BuildResults $BuildResults -BuildDir $BuildDir

# Create distribution packages
New-DistributionPackage -BuildDir $BuildDir -Version $version

# Run markdown linting on generated docs
Write-Host "`n[LINT] Running markdown linting on generated documentation..." -ForegroundColor Yellow
$GeneratedDocsPath = "$script:buildDir\Windows"
& "$PSScriptRoot\lint-markdown.ps1" -GeneratedPath "$GeneratedDocsPath/" -GeneratedReadmePath "$GeneratedDocsPath/README.md" -Fix
if ($LASTEXITCODE -ne 0) {
    exit 1
}

# Show build instructions
Show-BuildInstructions

# Cleanup temporary files
Invoke-BuildCleanup
