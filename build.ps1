# Generic Build Executables Script
# This script compiles the JiraUtil project into standalone executables for specified platforms
# Use platform-specific convenience scripts for common use cases:
#   - build-windows.ps1 (Windows only)
#   - build-macos.ps1 (macOS only) 
#   - build-linux.ps1 (Linux only)
#   - build-all.ps1 (All platforms)

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("windows", "macos", "linux", "all")]
    [string]$Platform,          # Target platform: "windows", "macos", "linux", or "all"
    [switch]$Clean = $false     # Clean build directories before building
)

$ErrorActionPreference = 'Stop'

Write-Host "[BUILD] Building JiraUtil Executables" -ForegroundColor Cyan
Write-Host "Platform: $Platform" -ForegroundColor Yellow

# Run unit tests FIRST - REQUIRED before any version changes
Write-Host "[TEST] Running unit tests..." -ForegroundColor Yellow
Write-Host "All tests must pass before building executables" -ForegroundColor Cyan

try {
    python tests/run_tests.py
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[FAIL] Unit tests failed! Build aborted." -ForegroundColor Red
        Write-Host "Please fix all test failures before building executables." -ForegroundColor Red
        exit 1
    }
    Write-Host "[OK] All unit tests passed! Proceeding with version management..." -ForegroundColor Green
} catch {
    Write-Host "[FAIL] Failed to run unit tests: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Please ensure the test environment is properly set up." -ForegroundColor Red
    exit 1
}

# Handle versioning AFTER tests pass
Write-Host "[VERSION] Managing version..." -ForegroundColor Yellow

# Check if code has changed and increment if needed
$versionResult = python version_manager.py increment-if-changed
$version = python version_manager.py get

if ($versionResult -match "incremented") {
    Write-Host "[OK] Version incremented: $version" -ForegroundColor Green
    # Update all files to new version
    python update-dev-version.py
    # Mark version update as complete to update hashes
    python -c "from version_manager import VersionManager; VersionManager().mark_version_update_complete()"
} else {
    Write-Host "[INFO] Version unchanged: $version (no code changes)" -ForegroundColor Yellow
}

# Create version info file
python create-version-info.py

# Check if PyInstaller is installed in virtual environment
Write-Host "[PACKAGE] Checking PyInstaller installation..." -ForegroundColor Yellow
try {
    $pyinstallerVersion = .\.venv\Scripts\python.exe -m PyInstaller --version 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller not found"
    }
    Write-Host "[OK] PyInstaller version: $pyinstallerVersion" -ForegroundColor Green
} catch {
    Write-Host "[FAIL] PyInstaller not found. Installing..." -ForegroundColor Red
    .\.venv\Scripts\python.exe -m pip install pyinstaller
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
$buildDir = "build-executables"
if (Test-Path $buildDir) {
    Remove-Item -Recurse -Force $buildDir
}
New-Item -ItemType Directory -Path $buildDir | Out-Null

# Function to build for a specific platform
function Build-Executable {
    param(
        [string]$PlatformName,
        [string]$TargetOS,
        [string]$IconPath = $null
    )
    
    Write-Host "`n[BUILD] Building for $PlatformName..." -ForegroundColor Cyan
    
    $outputDir = "$buildDir\$PlatformName"
    New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
    
    # Use the spec file for more control with virtual environment
    $pyinstallerCmd = @(
        ".\.venv\Scripts\python.exe", "-m", "PyInstaller"
        "JiraUtil.spec"
        "--distpath", $outputDir       # Override output directory
        "--workpath", "build"          # Temporary build directory
        "--noconfirm"                  # Don't ask for confirmation
    )
    
    # Execute PyInstaller
    Write-Host "Running: $($pyinstallerCmd -join ' ')" -ForegroundColor Gray
    & $pyinstallerCmd[0] $pyinstallerCmd[1..($pyinstallerCmd.Length-1)]
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] $PlatformName build completed successfully" -ForegroundColor Green
        
               # Copy additional files
               Copy-Item "jira_config_example.env" "$outputDir\jira_config.env" -ErrorAction SilentlyContinue
               
               # Create docs folder structure
               New-Item -ItemType Directory -Path "$outputDir\docs" -Force | Out-Null
               New-Item -ItemType Directory -Path "$outputDir\docs\shared" -Force | Out-Null
               
               # Create versioned README files
               $userReadme = Get-Content "user-guide.md" -Raw
               $userReadme = $userReadme -replace "# JiraUtil - User Guide", "# JiraUtil - User Guide`n`n## Version`n`nVersion: $version"
               # Remove trailing blank lines
               $userReadme = $userReadme.TrimEnd()
               $userReadme | Out-File -FilePath "$outputDir\README.md" -Encoding UTF8
               
               $commandReadme = Get-Content "docs\command-reference.md" -Raw
               $commandReadme = $commandReadme -replace "# Command Reference", "# Command Reference`n`n## Version`n`nVersion: $version"
               # Fix navigation for user environment (remove references to dev-only files)
               # No specific fixes needed for command-reference.md
               $commandReadme | Out-File -FilePath "$outputDir\docs\command-reference.md" -Encoding UTF8
               
               $troubleshootReadme = Get-Content "docs\troubleshooting.md" -Raw
               $troubleshootReadme = $troubleshootReadme -replace "# Troubleshooting Guide", "# Troubleshooting Guide`n`n## Version`n`nVersion: $version"
               # Fix navigation for user environment (remove references to dev-only files)
               $troubleshootReadme = $troubleshootReadme -replace "\[User Guide →\]\(\.\./user-guide\.md\)", "[End of User Documentation]"
               $troubleshootReadme | Out-File -FilePath "$outputDir\docs\troubleshooting.md" -Encoding UTF8
               
               # Copy and version shared documentation folder contents
               $sharedFiles = @("command-examples.md", "configuration.md", "file-structure.md", "test-fixture-pattern.md")
               foreach ($file in $sharedFiles) {
                   $sourceFile = "docs\shared\$file"
                   $targetFile = "$outputDir\docs\shared\$file"
                   if (Test-Path $sourceFile) {
                       $content = Get-Content $sourceFile -Raw
                       # Add version after the title (first # heading)
                       $content = $content -replace "(# [^`n]+)", "`$1`n`n## Version`n`nVersion: $version"
                       $content | Out-File -FilePath $targetFile -Encoding UTF8
                   }
               }
        
        # Create a simple launcher script for the platform
        if ($TargetOS -eq "windows") {
            $launcherContent = @"
@echo off
echo JiraUtil - Jira Administration Tool
echo ===================================
echo.
echo Edit jira_config.env with your Jira credentials, then run the tool.
echo.
pause
JiraUtil.exe %*
"@
            $launcherContent | Out-File -FilePath "$outputDir\run.bat" -Encoding ASCII
        } elseif ($TargetOS -eq "macos" -or $TargetOS -eq "linux") {
            $launcherContent = @"
#!/bin/bash
echo "JiraUtil - Jira Administration Tool"
echo "==================================="
echo ""
echo "Edit jira_config.env with your Jira credentials, then run the tool."
echo ""
read -p "Press Enter to continue..."
./JiraUtil "$@"
"@
            $launcherContent | Out-File -FilePath "$outputDir/run.sh" -Encoding UTF8
        }
        
        # Get executable size
        $exePath = if ($TargetOS -eq "windows") { "$outputDir\JiraUtil.exe" } else { "$outputDir/JiraUtil" }
        if (Test-Path $exePath) {
            $size = (Get-Item $exePath).Length
            $sizeMB = [math]::Round($size / 1MB, 2)
            Write-Host "[PACKAGE] Executable size: $sizeMB MB" -ForegroundColor Cyan
        }
        
    } else {
        Write-Host "[FAIL] $PlatformName build failed" -ForegroundColor Red
        return $false
    }
    
    return $true
}

# Build for requested platforms
$buildResults = @{}

if ($Platform -eq "all" -or $Platform -eq "windows") {
    $buildResults["Windows"] = Build-Executable -PlatformName "Windows" -TargetOS "windows"
}

if ($Platform -eq "all" -or $Platform -eq "macos") {
    $buildResults["macOS"] = Build-Executable -PlatformName "macOS" -TargetOS "macos"
}

if ($Platform -eq "all" -or $Platform -eq "linux") {
    $buildResults["Linux"] = Build-Executable -PlatformName "Linux" -TargetOS "linux"
}

# Summary
Write-Host "`n[SUMMARY] Build Summary" -ForegroundColor Cyan
Write-Host "===============" -ForegroundColor Cyan

foreach ($platform in $buildResults.Keys) {
    $status = if ($buildResults[$platform]) { "[OK] Success" } else { "[FAIL] Failed" }
    $color = if ($buildResults[$platform]) { "Green" } else { "Red" }
    Write-Host "$platform`: $status" -ForegroundColor $color
}

# Show output directories
Write-Host "`n[FILES] Output Directories:" -ForegroundColor Cyan
Get-ChildItem $buildDir -Directory | ForEach-Object {
    Write-Host "  - $($_.Name): $($_.FullName)" -ForegroundColor Yellow
}

# Create distribution package
Write-Host "`n[PACKAGE] Creating distribution packages..." -ForegroundColor Cyan

Get-ChildItem $buildDir -Directory | ForEach-Object {
    $platformName = $_.Name
    $platformDir = $_.FullName
    
    # Create ZIP archive with version number
    $zipPath = "$buildDir\JiraUtil-$platformName-v$version.zip"
    Write-Host "Creating $zipPath..." -ForegroundColor Gray
    
    # Use PowerShell's Compress-Archive
    Compress-Archive -Path "$platformDir\*" -DestinationPath $zipPath -Force
    
    if (Test-Path $zipPath) {
        $zipSize = (Get-Item $zipPath).Length
        $zipSizeMB = [math]::Round($zipSize / 1MB, 2)
        Write-Host "[OK] Created $zipPath ($zipSizeMB MB)" -ForegroundColor Green
    } else {
        Write-Host "[FAIL] Failed to create $zipPath" -ForegroundColor Red
    }
}

Write-Host "`n[SUCCESS] Build process completed!" -ForegroundColor Green
Write-Host "`n[VERSION] Next Steps:" -ForegroundColor Cyan
Write-Host "1. Test the executables in the build-executables directory" -ForegroundColor White
Write-Host "2. Distribute the ZIP files to target systems" -ForegroundColor White
Write-Host "3. Users should extract and configure jira_config.env" -ForegroundColor White
Write-Host "4. Run the executable or launcher script" -ForegroundColor White

Write-Host "`n[TIP] Usage Examples:" -ForegroundColor Cyan
Write-Host "Windows: .\JiraUtil.exe --help" -ForegroundColor White
Write-Host "macOS/Linux: ./JiraUtil --help" -ForegroundColor White
