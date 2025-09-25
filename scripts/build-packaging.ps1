# Build Packaging Functions
# This script contains functions for packaging and distributing built executables

function New-DistributionPackage {
    <#
    .SYNOPSIS
    Creates distribution packages for built executables.
    
    .DESCRIPTION
    Creates ZIP archives for each platform's built executable with version numbers.
    
    .PARAMETER BuildDir
    The build directory containing platform subdirectories.
    
    .PARAMETER Version
    The version string to include in package names.
    
    .EXAMPLE
    New-DistributionPackage -BuildDir "build-executables" -Version "1.0.0"
    #>
    
    param(
        [string]$BuildDir,
        [string]$Version
    )
    
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
}

function Show-BuildSummary {
    <#
    .SYNOPSIS
    Displays a summary of the build results.
    
    .DESCRIPTION
    Shows which platforms built successfully and displays output directories.
    
    .PARAMETER BuildResults
    Hashtable containing build results for each platform.
    
    .PARAMETER BuildDir
    The build directory containing platform subdirectories.
    
    .EXAMPLE
    Show-BuildSummary -BuildResults $results -BuildDir "build-executables"
    #>
    
    param(
        [hashtable]$BuildResults,
        [string]$BuildDir
    )
    
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
}

function Show-BuildInstructions {
    <#
    .SYNOPSIS
    Displays post-build instructions and usage examples.
    
    .DESCRIPTION
    Shows next steps for testing and distributing the built executables.
    #>
    
    Write-Host "`n[SUCCESS] Build process completed!" -ForegroundColor Green
    Write-Host "`n[VERSION] Next Steps:" -ForegroundColor Cyan
    Write-Host "1. Test the executables in the build-executables directory" -ForegroundColor White
    Write-Host "2. Distribute the ZIP files to target systems" -ForegroundColor White
    Write-Host "3. Users should extract and configure jira_config.env" -ForegroundColor White
    Write-Host "4. Run the executable or launcher script" -ForegroundColor White

    Write-Host "`n[TIP] Usage Examples:" -ForegroundColor Cyan
    Write-Host "Windows: .\JiraUtil.exe --help" -ForegroundColor White
}

function Invoke-BuildCleanup {
    <#
    .SYNOPSIS
    Cleans up temporary files created during the build process.
    
    .DESCRIPTION
    Removes temporary files that were created during the build but are not needed
    in the final distribution.
    #>
    
    Write-Host "`n[CLEANUP] Cleaning up temporary files..." -ForegroundColor Yellow
    
    $tempFiles = @("version_info.txt", "JiraUtil.spec")
    
    foreach ($file in $tempFiles) {
        if (Test-Path $file) {
            Remove-Item $file -Force
            Write-Host "[OK] Removed $file" -ForegroundColor Green
        }
    }
}
