# Linux Build Convenience Script
# This script builds Linux executables by calling the generic build script

Write-Host "🔨 Building JiraUtil for Linux" -ForegroundColor Cyan
Write-Host "Calling generic build script with Linux platform..." -ForegroundColor Yellow

# Call the generic build script with Linux platform
& .\build.ps1 -Platform linux @args

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Linux build completed successfully!" -ForegroundColor Green
} else {
    Write-Host "❌ Linux build failed!" -ForegroundColor Red
    exit $LASTEXITCODE
}
