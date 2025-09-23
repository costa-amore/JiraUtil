# All Platforms Build Convenience Script
# This script builds executables for all platforms by calling the generic build script

Write-Host "🔨 Building JiraUtil for All Platforms" -ForegroundColor Cyan
Write-Host "Calling generic build script with all platforms..." -ForegroundColor Yellow

# Call the generic build script with all platforms
& .\scripts\build.ps1 -Platform all @args

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ All platforms build completed successfully!" -ForegroundColor Green
} else {
    Write-Host "❌ All platforms build failed!" -ForegroundColor Red
    exit $LASTEXITCODE
}
