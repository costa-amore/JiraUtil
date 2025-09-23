# macOS Build Convenience Script
# This script builds macOS executables by calling the generic build script

Write-Host "🔨 Building JiraUtil for macOS" -ForegroundColor Cyan
Write-Host "Calling generic build script with macOS platform..." -ForegroundColor Yellow

# Call the generic build script with macOS platform
& .\build.ps1 -Platform macos @args

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ macOS build completed successfully!" -ForegroundColor Green
} else {
    Write-Host "❌ macOS build failed!" -ForegroundColor Red
    exit $LASTEXITCODE
}
