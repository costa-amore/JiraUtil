# Build Executables Script
# This script compiles the JiraUtil project into standalone executables for multiple platforms

param(
    [string]$Platform = "all",  # "windows", "macos", "linux", or "all"
    [switch]$Clean = $false     # Clean build directories before building
)

$ErrorActionPreference = 'Stop'

Write-Host "🔨 Building JiraUtil Executables" -ForegroundColor Cyan
Write-Host "Platform: $Platform" -ForegroundColor Yellow

# Check if PyInstaller is installed in virtual environment
Write-Host "📦 Checking PyInstaller installation..." -ForegroundColor Yellow
try {
    $pyinstallerVersion = .\.venv\Scripts\python.exe -m PyInstaller --version 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller not found"
    }
    Write-Host "✅ PyInstaller version: $pyinstallerVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ PyInstaller not found. Installing..." -ForegroundColor Red
    .\.venv\Scripts\python.exe -m pip install pyinstaller
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to install PyInstaller" -ForegroundColor Red
        exit 1
    }
    Write-Host "✅ PyInstaller installed successfully" -ForegroundColor Green
}

# Clean build directories if requested
if ($Clean) {
    Write-Host "🧹 Cleaning build directories..." -ForegroundColor Yellow
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
    
    Write-Host "`n🔨 Building for $PlatformName..." -ForegroundColor Cyan
    
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
        Write-Host "✅ $PlatformName build completed successfully" -ForegroundColor Green
        
        # Copy additional files
        Copy-Item "jira_config_example.env" "$outputDir\jira_config.env" -ErrorAction SilentlyContinue
        Copy-Item "README.md" "$outputDir\" -ErrorAction SilentlyContinue
        Copy-Item "docs" "$outputDir\" -Recurse -ErrorAction SilentlyContinue
        
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
            Write-Host "📦 Executable size: $sizeMB MB" -ForegroundColor Cyan
        }
        
    } else {
        Write-Host "❌ $PlatformName build failed" -ForegroundColor Red
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
Write-Host "`n📊 Build Summary" -ForegroundColor Cyan
Write-Host "===============" -ForegroundColor Cyan

foreach ($platform in $buildResults.Keys) {
    $status = if ($buildResults[$platform]) { "✅ Success" } else { "❌ Failed" }
    $color = if ($buildResults[$platform]) { "Green" } else { "Red" }
    Write-Host "$platform`: $status" -ForegroundColor $color
}

# Show output directories
Write-Host "`n📁 Output Directories:" -ForegroundColor Cyan
Get-ChildItem $buildDir -Directory | ForEach-Object {
    Write-Host "  - $($_.Name): $($_.FullName)" -ForegroundColor Yellow
}

# Create distribution package
Write-Host "`n📦 Creating distribution packages..." -ForegroundColor Cyan

Get-ChildItem $buildDir -Directory | ForEach-Object {
    $platformName = $_.Name
    $platformDir = $_.FullName
    
    # Create ZIP archive
    $zipPath = "$buildDir\JiraUtil-$platformName.zip"
    Write-Host "Creating $zipPath..." -ForegroundColor Gray
    
    # Use PowerShell's Compress-Archive
    Compress-Archive -Path "$platformDir\*" -DestinationPath $zipPath -Force
    
    if (Test-Path $zipPath) {
        $zipSize = (Get-Item $zipPath).Length
        $zipSizeMB = [math]::Round($zipSize / 1MB, 2)
        Write-Host "✅ Created $zipPath ($zipSizeMB MB)" -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to create $zipPath" -ForegroundColor Red
    }
}

Write-Host "`n🎉 Build process completed!" -ForegroundColor Green
Write-Host "`n📋 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Test the executables in the build-executables directory" -ForegroundColor White
Write-Host "2. Distribute the ZIP files to target systems" -ForegroundColor White
Write-Host "3. Users should extract and configure jira_config.env" -ForegroundColor White
Write-Host "4. Run the executable or launcher script" -ForegroundColor White

Write-Host "`n💡 Usage Examples:" -ForegroundColor Cyan
Write-Host "Windows: .\JiraUtil.exe --help" -ForegroundColor White
Write-Host "macOS/Linux: ./JiraUtil --help" -ForegroundColor White
