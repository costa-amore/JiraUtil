# Generic Build Executables Script
# This script compiles the JiraUtil project into standalone executables for specified platforms
# Use platform-specific convenience scripts for common use cases:
#   - build-windows.ps1 (Windows only)
#   - build-all.ps1 (All platforms - currently Windows only)
#   
# Note: macOS and Linux builds are temporarily disabled

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("windows", "all")]
    [string]$Platform,          # Target platform: "windows" or "all" (Windows only for now)
    [switch]$Clean = $false,    # Clean build directories before building
    [switch]$BuildForRelease = $false  # Build for release (increment build number)
)

$ErrorActionPreference = 'Stop'

Write-Host "[BUILD] Building JiraUtil Executables" -ForegroundColor Cyan
Write-Host "Platform: $Platform" -ForegroundColor Yellow

# Run unit tests FIRST - REQUIRED before any version changes
Write-Host "[TEST] Running unit tests..." -ForegroundColor Yellow
Write-Host "All tests must pass before building executables" -ForegroundColor Cyan

try {
    # Run tests directly with pytest for real-time output
    # Use Start-Process to avoid PowerShell output buffering
    $process = Start-Process -FilePath "python" -ArgumentList "-m", "pytest", "tests/", "-v", "--tb=short" -Wait -PassThru -NoNewWindow
    if ($process.ExitCode -ne 0) {
        Write-Host "[FAIL] Unit tests failed! Build aborted." -ForegroundColor Red
        Write-Host "Please fix all test failures before building executables." -ForegroundColor Red
        exit 1
    }
    Write-Host "[OK] All unit tests passed! Proceeding with markdown linting..." -ForegroundColor Green
} catch {
    Write-Host "[FAIL] Failed to run unit tests: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Please ensure the test environment is properly set up." -ForegroundColor Red
    exit 1
}

# Run markdown linting on source docs
Write-Host "[LINT] Running markdown linting on source documentation..." -ForegroundColor Yellow
& "$PSScriptRoot\lint-markdown.ps1" -SourcePath "docs/" -ReadmePath "README.md" -Fix
if ($LASTEXITCODE -ne 0) {
    exit 1
}

# Handle versioning AFTER tests pass
Write-Host "[VERSION] Managing version..." -ForegroundColor Yellow

# Determine build context automatically
$IsCI = $env:CI -eq "true" -or $env:GITHUB_ACTIONS -eq "true"
$IsRelease = $BuildForRelease -eq $true

if ($IsRelease) {
    # Release build: always increment build number
    Write-Host "[INFO] Release build - incrementing build number" -ForegroundColor Cyan
    $VersionResult = python tools\version_manager.py build release --version-file scripts/version.json
    $version = python tools\version_manager.py get --version-file scripts/version.json
    Write-Host "[OK] Release build incremented: $version" -ForegroundColor Green
    
    # Update all files to new version
    python tools\update-dev-version.py
    # Mark version update as complete to update hashes
    python -c "import sys; sys.path.insert(0, 'tools'); from version_manager import VersionManager; VersionManager('scripts/version.json').mark_version_update_complete()"
} elseif ($IsCI) {
    # CI build: use version as-is (release script already incremented it)
    Write-Host "[INFO] CI build - using existing version" -ForegroundColor Cyan
    $version = python tools\version_manager.py get --version-file scripts/version.json
    Write-Host "[INFO] CI build using version: $version" -ForegroundColor Cyan
} else {
    # Local build: increment local build number if code changed
    Write-Host "[INFO] Local build - incrementing local build number if code changed" -ForegroundColor Yellow
    $VersionResult = python tools\version_manager.py increment-local-if-changed --version-file scripts/version.json
    $version = python tools\version_manager.py get --version-file scripts/version.json
    
    if ($VersionResult -match "incremented") {
        Write-Host "[OK] Local build incremented: $version" -ForegroundColor Green
        # Update all files to new version
        python tools\update-dev-version.py
        # Mark version update as complete to update hashes
        python -c "import sys; sys.path.insert(0, 'tools'); from version_manager import VersionManager; VersionManager('scripts/version.json').mark_version_update_complete()"
    } else {
        Write-Host "[INFO] Local build unchanged: $version (no code changes)" -ForegroundColor Yellow
    }
}

# Create version info file
python tools\create-version-info.py scripts\version.json version_info.txt

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

# Function to convert relative links for built executable environment
function Convert-LinksForBuiltExecutable {
    param(
        [string]$Content,
        [string]$DocsFolderName = "docs"
    )
    
    # Convert relative links to docs/ format for built executable
    # (README.md is in root, so links need docs/ prefix)
    $Content = $Content -replace "\[Configuration Reference\]\(shared/configuration\.md\)", "[Configuration Reference]($DocsFolderName/shared/configuration.md)"
    $Content = $Content -replace "\[Command Examples Reference\]\(shared/command-examples\.md\)", "[Command Examples Reference]($DocsFolderName/shared/command-examples.md)"
    $Content = $Content -replace "\[Test Fixture Pattern Reference\]\(shared/test-fixture-pattern\.md\)", "[Test Fixture Pattern Reference]($DocsFolderName/shared/test-fixture-pattern.md)"
    $Content = $Content -replace "\[File Structure Reference\]\(shared/file-structure\.md\)", "[File Structure Reference]($DocsFolderName/shared/file-structure.md)"
    $Content = $Content -replace "\[Command Reference\]\(command-reference\.md\)", "[Command Reference]($DocsFolderName/command-reference.md)"
    $Content = $Content -replace "\[Troubleshooting Guide\]\(troubleshooting\.md\)", "[Troubleshooting Guide]($DocsFolderName/troubleshooting.md)"
    
    return $Content
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
               
               # Create docs folder structure
               New-Item -ItemType Directory -Path "$OutputDir\docs" -Force | Out-Null
               New-Item -ItemType Directory -Path "$OutputDir\docs\shared" -Force | Out-Null
               
               # Create versioned README files
               $UserReadme = Get-Content "docs\user-guide.md" -Raw
               # Add version only if not already present
               if ($UserReadme -notmatch "## Version") {
                   $UserReadme = $UserReadme -replace "# JiraUtil - User Guide", "# JiraUtil - User Guide`n`n## Version`n`nVersion: $version"
               }
               # Convert links for built executable environment
               $UserReadme = Convert-LinksForBuiltExecutable -Content $UserReadme -DocsFolderName "docs"
               # Remove trailing blank lines
               $UserReadme = $UserReadme.TrimEnd()
               $UserReadme | Out-File -FilePath "$OutputDir\README.md" -Encoding UTF8
               
               $CommandReadme = Get-Content "docs\command-reference.md" -Raw
               # Add version only if not already present (look for actual version chapter, not command descriptions)
               if ($CommandReadme -notmatch "## Version`n`nVersion:") {
                   $CommandReadme = $CommandReadme -replace "# Command Reference", "# Command Reference`n`n## Version`n`nVersion: $version"
               }
               # Fix navigation for user environment (remove references to dev-only files)
               $CommandReadme = $CommandReadme -replace "\[← Release and Versioning\]\(release-and-versioning\.md\)", "[← Building Executables](building-executables.md)"
               # Remove trailing blank lines
               $CommandReadme = $CommandReadme.TrimEnd()
               $CommandReadme | Out-File -FilePath "$OutputDir\docs\command-reference.md" -Encoding UTF8
               
               # Copy building-executables.md for user reference
               $BuildingReadme = Get-Content "docs\building-executables.md" -Raw
               # Add version only if not already present
               if ($BuildingReadme -notmatch "## Version") {
                   $BuildingReadme = $BuildingReadme -replace "# Building Executables", "# Building Executables`n`n## Version`n`nVersion: $version"
               }
               # Fix navigation for user environment (remove references to dev-only files)
               $BuildingReadme = $BuildingReadme -replace "\[← Testing\]\(testing\.md\)", "[← User Guide](../README.md)"
               $BuildingReadme = $BuildingReadme -replace "\[Release and Versioning →\]\(release-and-versioning\.md\)", "[Command Reference →](command-reference.md)"
               # Remove trailing blank lines
               $BuildingReadme = $BuildingReadme.TrimEnd()
               $BuildingReadme | Out-File -FilePath "$OutputDir\docs\building-executables.md" -Encoding UTF8
               
               $TroubleshootReadme = Get-Content "docs\troubleshooting.md" -Raw
               # Add version only if not already present
               if ($TroubleshootReadme -notmatch "## Version") {
                   $TroubleshootReadme = $TroubleshootReadme -replace "# Troubleshooting Guide", "# Troubleshooting Guide`n`n## Version`n`nVersion: $version"
               }
               # Fix navigation for user environment (remove references to dev-only files)
               $TroubleshootReadme = $TroubleshootReadme -replace "\[User Guide →\]\(\.\./user-guide\.md\)", "[End of User Documentation]"
               # Remove trailing blank lines
               $TroubleshootReadme = $TroubleshootReadme.TrimEnd()
               $TroubleshootReadme | Out-File -FilePath "$OutputDir\docs\troubleshooting.md" -Encoding UTF8
               
               # Copy and version shared documentation folder contents
               $SharedFiles = @("command-examples.md", "configuration.md", "file-structure.md", "test-fixture-pattern.md")
               foreach ($file in $SharedFiles) {
                   $SourceFile = "docs\shared\$file"
                   $TargetFile = "$OutputDir\docs\shared\$file"
                   if (Test-Path $SourceFile) {
                       $content = Get-Content $SourceFile -Raw
                       # Add version after the title (first # heading) only if not already present
                       if ($content -notmatch "## Version") {
                           $content = $content -replace "^# [^`n]+", "`$&`n`n## Version`n`nVersion: $version"
                       }
                       # Remove trailing blank lines
                       $content = $content.TrimEnd()
                       $content | Out-File -FilePath $TargetFile -Encoding UTF8
                   }
               }
        
        # Create a simple launcher script for the platform
        if ($TargetOS -eq "windows") {
            $LauncherContent = @"
@echo off
echo JiraUtil - Jira Administration Tool
echo ===================================
echo.
echo Edit jira_config.env with your Jira credentials, then run the tool.
echo.
pause
JiraUtil.exe %*
"@
            $LauncherContent | Out-File -FilePath "$OutputDir\run.bat" -Encoding ASCII
        } elseif ($TargetOS -eq "macos" -or $TargetOS -eq "linux") {
            $LauncherContent = @"
#!/bin/bash
echo "JiraUtil - Jira Administration Tool"
echo "==================================="
echo ""
echo "Edit jira_config.env with your Jira credentials, then run the tool."
echo ""
read -p "Press Enter to continue..."
./JiraUtil "$@"
"@
            $LauncherContent | Out-File -FilePath "$OutputDir/run.sh" -Encoding UTF8
        }
        
        # Get executable size
        $ExePath = if ($TargetOS -eq "windows") { "$OutputDir\JiraUtil.exe" } else { "$OutputDir/JiraUtil" }
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

if ($Platform -eq "all" -or $Platform -eq "windows") {
    $BuildResults["Windows"] = Build-Executable -PlatformName "Windows" -TargetOS "windows"
}

# Note: macOS and Linux builds are temporarily disabled
# if ($Platform -eq "all" -or $Platform -eq "macos") {
#     $BuildResults["macOS"] = Build-Executable -PlatformName "macOS" -TargetOS "macos"
# }

# if ($Platform -eq "all" -or $Platform -eq "linux") {
#     $BuildResults["Linux"] = Build-Executable -PlatformName "Linux" -TargetOS "linux"
# }

# Summary
Write-Host "`n[SUMMARY] Build Summary" -ForegroundColor Cyan
Write-Host "===============" -ForegroundColor Cyan

foreach ($platform in $BuildResults.Keys) {
    $status = if ($BuildResults[$platform]) { "[OK] Success" } else { "[FAIL] Failed" }
    $color = if ($BuildResults[$platform]) { "Green" } else { "Red" }
    Write-Host "$platform`: $status" -ForegroundColor $color
}

# Show output directories
Write-Host "`n[FILES] Output Directories:" -ForegroundColor Cyan
Get-ChildItem $BuildDir -Directory | ForEach-Object {
    Write-Host "  - $($_.Name): $($_.FullName)" -ForegroundColor Yellow
}

# Create distribution package
Write-Host "`n[PACKAGE] Creating distribution packages..." -ForegroundColor Cyan

Get-ChildItem $BuildDir -Directory | ForEach-Object {
    $PlatformName = $_.Name
    $PlatformDir = $_.FullName
    
    # Create ZIP archive with version number
    $ZipPath = "$BuildDir\JiraUtil-$PlatformName-v$version.zip"
    Write-Host "Creating $ZipPath..." -ForegroundColor Gray
    
    # Use PowerShell's Compress-Archive
    Compress-Archive -Path "$PlatformDir\*" -DestinationPath $ZipPath -Force
    
    if (Test-Path $ZipPath) {
        $ZipSize = (Get-Item $ZipPath).Length
        $ZipSizeMB = [math]::Round($ZipSize / 1MB, 2)
        Write-Host "[OK] Created $ZipPath ($ZipSizeMB MB)" -ForegroundColor Green
    } else {
        Write-Host "[FAIL] Failed to create $ZipPath" -ForegroundColor Red
    }
}

# Run markdown linting on generated docs
Write-Host "`n[LINT] Running markdown linting on generated documentation..." -ForegroundColor Yellow
$GeneratedDocsPath = "$script:buildDir\Windows"
& "$PSScriptRoot\lint-markdown.ps1" -GeneratedPath "$GeneratedDocsPath/" -GeneratedReadmePath "$GeneratedDocsPath/README.md" -Fix
if ($LASTEXITCODE -ne 0) {
    exit 1
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

# Cleanup temporary files
Write-Host "`n[CLEANUP] Cleaning up temporary files..." -ForegroundColor Yellow
if (Test-Path "version_info.txt") {
    Remove-Item "version_info.txt" -Force
    Write-Host "[OK] Removed version_info.txt" -ForegroundColor Green
}
if (Test-Path "JiraUtil.spec") {
    Remove-Item "JiraUtil.spec" -Force
    Write-Host "[OK] Removed JiraUtil.spec" -ForegroundColor Green
}
