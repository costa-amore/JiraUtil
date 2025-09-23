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
    Target platform: "windows", "macos", "linux", or "all"
    
.PARAMETER Clean
    Clean build directories before building

.PARAMETER Message
    Custom commit message for the version increment

.EXAMPLE
    .\release.ps1 -Platform windows
    .\release.ps1 -Platform all -Message "Release v1.0.32 with new features"
#>

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("windows", "macos", "linux", "all")]
    [string]$Platform,          # Target platform: "windows", "macos", "linux", or "all"
    [switch]$Clean = $false,    # Clean build directories before building
    [string]$Message = ""       # Custom commit message
)

$ErrorActionPreference = 'Stop'

Write-Host "🚀 Creating JiraUtil Release" -ForegroundColor Cyan
Write-Host "Platform: $Platform" -ForegroundColor Yellow

# Check if we're in a git repository
if (-not (Test-Path ".git")) {
    Write-Host "[ERROR] Not in a git repository!" -ForegroundColor Red
    exit 1
}

# Check if there are uncommitted changes (allow local build files)
$gitStatus = git status --porcelain
if ($gitStatus) {
    # Filter out local build files that will be overridden
    $localBuildFiles = @("scripts/version.json", "README.md", ".code_hash", "scripts/release.ps1")
    $relevantChanges = $gitStatus | Where-Object { 
        $file = ($_ -split '\s+')[1]
        $localBuildFiles -notcontains $file
    }
    
    if ($relevantChanges) {
        Write-Host "[ERROR] You have uncommitted changes that are not local build files. Please commit or stash them first." -ForegroundColor Red
        Write-Host "Uncommitted files:" -ForegroundColor Yellow
        Write-Host $relevantChanges -ForegroundColor Gray
        exit 1
    } else {
        Write-Host "[INFO] Found local build changes that will be overridden by release process" -ForegroundColor Yellow
    }
}

# Get current version
$currentVersion = python tools\version_manager.py get --version-file scripts/version.json
Write-Host "[INFO] Current version: $currentVersion" -ForegroundColor Cyan

# Build with version increment
Write-Host "`n[BUILD] Building with version increment..." -ForegroundColor Yellow
& .\scripts\build.ps1 -Platform $Platform -Clean:$Clean -BuildForRelease

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Build failed! Release aborted." -ForegroundColor Red
    exit 1
}

# Get new version
$newVersion = python tools\version_manager.py get --version-file scripts/version.json
Write-Host "`n[VERSION] Version incremented: $currentVersion → $newVersion" -ForegroundColor Green

# Check if version actually changed
if ($currentVersion -eq $newVersion) {
    Write-Host "[WARN] Version did not change. This might mean no code changes were detected." -ForegroundColor Yellow
    Write-Host "Do you want to continue anyway? (y/N): " -ForegroundColor Yellow -NoNewline
    $response = Read-Host
    if ($response -ne "y" -and $response -ne "Y") {
        Write-Host "[INFO] Release cancelled by user." -ForegroundColor Yellow
        exit 0
    }
}

# Create commit message
if ($Message -eq "") {
    $Message = "chore: release version $newVersion"
}

# Commit version changes
Write-Host "`n[GIT] Committing version changes..." -ForegroundColor Yellow
git add scripts\version.json README.md build\version_info.txt .code_hash
git commit -m $Message

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Failed to commit version changes!" -ForegroundColor Red
    exit 1
}

Write-Host "[OK] Version changes committed" -ForegroundColor Green

# Create release tag
Write-Host "`n[TAG] Creating release tag v$newVersion..." -ForegroundColor Yellow
git tag -a "v$newVersion" -m "Release v$newVersion"

# Push commit and tag together atomically
Write-Host "`n[GIT] Pushing commit and tag to CI..." -ForegroundColor Yellow
git push --follow-tags

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Failed to push commit and tag!" -ForegroundColor Red
    exit 1
}

Write-Host "[OK] Commit and tag v$newVersion pushed successfully" -ForegroundColor Green

# Summary
Write-Host "`n🎉 Release Process Complete!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Gray
Write-Host "Version: $currentVersion → $newVersion" -ForegroundColor White
Write-Host "Platform: $Platform" -ForegroundColor White
Write-Host "Status: Pushed to CI" -ForegroundColor White
Write-Host "`n[INFO] CI will now:" -ForegroundColor Cyan
Write-Host "  - Build the executables (already done locally)" -ForegroundColor White
Write-Host "  - Create GitHub release v$newVersion (triggered by tag)" -ForegroundColor White
Write-Host "  - Upload artifacts" -ForegroundColor White
Write-Host "`n[LINK] Check progress: https://github.com/costa-amore/JiraUtil/actions" -ForegroundColor Blue
