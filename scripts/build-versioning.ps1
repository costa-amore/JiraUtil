# Build Versioning Functions
# This script contains functions for managing version numbers during the build process

function Invoke-VersionManagement {
    <#
    .SYNOPSIS
    Manages version numbers based on build context.
    
    .DESCRIPTION
    Handles version incrementing for different build contexts:
    - Release builds: Always increment build number
    - CI builds: Use existing version (already incremented by release script)
    - Local builds: Increment local build number only if code changed
    
    .PARAMETER IsRelease
    Whether this is a release build.
    
    .PARAMETER IsCI
    Whether this is running in CI environment.
    
    .OUTPUTS
    Returns the current version string.
    #>
    
    param(
        [bool]$IsRelease,
        [bool]$IsCI
    )
    
    Write-Host "[VERSION] Managing version..." -ForegroundColor Yellow
    
    if ($IsRelease) {
        # Release build: always increment build number
        Write-Host "[INFO] Release build - incrementing build number" -ForegroundColor Cyan
        $VersionResult = python tools\version_manager.py build release --version-file scripts/version.json
        $version = python tools\version_manager.py get --version-file scripts/version.json
        Write-Host "[OK] Release build incremented: $version" -ForegroundColor Green
        
        # Update all files to new version
        python tools\update-dev-version.py | Out-Null
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
            python tools\update-dev-version.py | Out-Null
            # Mark version update as complete to update hashes
            python -c "import sys; sys.path.insert(0, 'tools'); from version_manager import VersionManager; VersionManager('scripts/version.json').mark_version_update_complete()"
        } else {
            Write-Host "[INFO] Local build unchanged: $version (no code changes)" -ForegroundColor Yellow
        }
    }
    
    return $version
}

function New-VersionInfoFile {
    <#
    .SYNOPSIS
    Creates version info file for PyInstaller.
    
    .DESCRIPTION
    Generates a version info file that PyInstaller can use to embed version information
    into the executable.
    
    .PARAMETER VersionFile
    Path to the version JSON file.
    
    .PARAMETER OutputFile
    Path where the version info file should be created.
    #>
    
    param(
        [string]$VersionFile = "scripts/version.json",
        [string]$OutputFile = "version_info.txt"
    )
    
    Write-Host "[VERSION] Creating version info file..." -ForegroundColor Yellow
    python tools\create-version-info.py $VersionFile $OutputFile
}
