# Windows Build Convenience Script
# This script builds Windows executables by calling the generic build script

Write-Host "🔨 Building JiraUtil for Windows" -ForegroundColor Cyan
Write-Host "Calling generic build script with Windows platform..." -ForegroundColor Yellow

# Call the generic build script with Windows platform
& .\scripts\build.ps1 -Platform windows @args

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Windows build completed successfully!" -ForegroundColor Green
} else {
    Write-Host "❌ Windows build failed!" -ForegroundColor Red
    exit $LASTEXITCODE
}