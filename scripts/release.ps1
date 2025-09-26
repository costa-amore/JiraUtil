#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Create a release by incrementing version, building, and pushing to CI

.DESCRIPTION
    This script creates a release by:
    1. Incrementing the version number
    2. Building the executables
    3. Committing the version changes
    4. Pushing to CI to create the release

.PARAMETER Platform
    Target platform: "windows" (only Windows is supported)
    
.PARAMETER Clean
    Clean build directories before building

.PARAMETER Message
    Custom commit message for the version increment

.EXAMPLE
    .\release.ps1 -Platform windows
    .\release.ps1 -Platform windows -Message "Release v1.0.32 with new features"
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$Platform,          # Target platform: "windows" (only Windows is supported)
    [switch]$Clean = $false,    # Clean build directories before building
    [string]$Message = ""       # Custom commit message
)

$ErrorActionPreference = 'Stop'

# =============================================================================
# COLOR SYSTEM (Reusing Python color system)
# =============================================================================

# Import the centralized color utilities
. "$PSScriptRoot\color_utils.ps1"

# =============================================================================
# VALIDATION FUNCTIONS
# =============================================================================

function Test-Platform {
    param([string]$Platform)
    
    # Normalize platform to lowercase for case-insensitive comparison
    $normalizedPlatform = $Platform.ToLower()
    
    if ($normalizedPlatform -ne "windows") {
        Write-Fail "Unsupported platform '$Platform'"
        Write-Host ""
        Write-Fail "JiraUtil only supports Windows builds."
        Write-Host "   Use: .\scripts\release.ps1 -Platform windows" -ForegroundColor Yellow
        Write-Host ""
        Write-Info "Supported platforms:"
        Write-Host "   - windows (only option)" -ForegroundColor White
        Write-Host ""
        Write-Fail "Aborting release process."
        return $false
    }
    return $true
}

function Test-GitRepository {
    if (-not (Test-Path ".git")) {
        Write-Fail "Not in a git repository!"
        return $false
    }
    return $true
}

function Test-UncommittedChanges {
    $gitStatus = git status --porcelain
    if ($gitStatus) {
        # Filter out local build files that will be overridden
        $localBuildFiles = @("scripts/version.json", "README.md", ".code_hash", "scripts/release.ps1")
        $relevantChanges = $gitStatus | Where-Object { 
            $file = ($_ -split '\s+')[1]
            $localBuildFiles -notcontains $file
        }
        
        if ($relevantChanges) {
            Write-Fail "You have uncommitted changes that are not local build files. Please commit or stash them first."
            Write-Host "Uncommitted files:" -ForegroundColor Yellow
            Write-Host $relevantChanges -ForegroundColor Gray
            return $false
        } else {
            Write-Info "Found local build changes that will be overridden by release process"
        }
    }
    return $true
}

# =============================================================================
# VERSION FUNCTIONS
# =============================================================================

function Get-CurrentVersion {
    return python tools\version_manager.py get --version-file scripts/version.json
}

function Get-NewVersion {
    return python tools\version_manager.py get --version-file scripts/version.json
}

# =============================================================================
# BUILD FUNCTIONS
# =============================================================================

function Invoke-ReleaseBuild {
    param([string]$Platform, [bool]$Clean)
    
    # Run the build with version increment (includes linting)
    Write-Build "Building with version increment..."
    & .\scripts\build.ps1 -Platform $Platform -Clean:$Clean -BuildForRelease
    
    if ($LASTEXITCODE -ne 0) {
        Write-Fail "Build failed! Release aborted."
        return $false
    }
    return $true
}



# =============================================================================
# GIT FUNCTIONS
# =============================================================================

function Invoke-GitCommit {
    param([string]$Message)
    
    Write-Git "Committing version changes..."
    git add scripts\version.json README.md build\version_info.txt .code_hash
    git commit -m $Message
    
    if ($LASTEXITCODE -ne 0) {
        Write-Fail "Failed to commit version changes!"
        return $false
    }
    
    Write-OK "Version changes committed"
    return $true
}

function Invoke-GitTag {
    param([string]$Version)
    
    Write-Tag "Creating release tag v$Version..."
    git tag -a "v$Version" -m "Release v$Version"
    return $true
}

function Invoke-GitPush {
    Write-Git "Pushing commit and tag to CI..."
    git push --follow-tags
    
    if ($LASTEXITCODE -ne 0) {
        Write-Fail "Failed to push commit and tag!"
        return $false
    }
    
    Write-OK "Commit and tag pushed successfully"
    return $true
}

# =============================================================================
# MAIN RELEASE LOGIC
# =============================================================================

function Start-ReleaseProcess {
    param([string]$Platform, [bool]$Clean, [string]$Message)
    
    # Validate platform
    if (-not (Test-Platform $Platform)) {
        return $false
    }
    
    # Validate git repository
    if (-not (Test-GitRepository)) {
        return $false
    }
    
    # Validate uncommitted changes - abort if any exist
    if (-not (Test-UncommittedChanges)) {
        return $false
    }
    
    # Get current version
    $currentVersion = Get-CurrentVersion
    Write-Info "Current version: $currentVersion"
    
    # Build with version increment
    if (-not (Invoke-ReleaseBuild $Platform $Clean)) {
        return $false
    }
    
    # Get new version
    $newVersion = Get-NewVersion
    Write-Version "Version incremented: $currentVersion -> $newVersion"
    
    # Check if version actually changed
    if ($currentVersion -eq $newVersion) {
        Write-Warn "Version did not change. This might mean no code changes were detected."
        Write-Host "Do you want to continue anyway? (y/N): " -ForegroundColor Yellow -NoNewline
        $response = Read-Host
        if ($response -ne "y" -and $response -ne "Y") {
            Write-Info "Release cancelled by user."
            return $false
        }
    }
    
    # Create commit message
    if ($Message -eq "") {
        $Message = "chore: release version $newVersion"
    }
    
    # Commit version changes
    if (-not (Invoke-GitCommit $Message)) {
        return $false
    }
    
    # Create release tag
    Invoke-GitTag $newVersion
    
    # Push commit and tag together atomically
    if (-not (Invoke-GitPush)) {
        return $false
    }
    
    # Summary
    Write-Success "Release Process Complete!"
    Write-Host "================================" -ForegroundColor Gray
    Write-Host "Version: $currentVersion -> $newVersion" -ForegroundColor White
    Write-Host "Platform: $Platform" -ForegroundColor White
    Write-Host "Status: Pushed to CI" -ForegroundColor White
    Write-Info "CI will now:"
    Write-Host "  - Build the executables (already done locally)" -ForegroundColor White
    Write-Host "  - Create GitHub release v$newVersion (triggered by tag)" -ForegroundColor White
    Write-Host "  - Upload artifacts" -ForegroundColor White
    Write-Link "Check progress: https://github.com/costa-amore/JiraUtil/actions"
    
    return $true
}

# =============================================================================
# SCRIPT ENTRY POINT
# =============================================================================

Write-Info "Creating JiraUtil Release"
Write-Host "Platform: $Platform" -ForegroundColor Yellow

# Run the release process
if (-not (Start-ReleaseProcess $Platform $Clean $Message)) {
    exit 1
}
