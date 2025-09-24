# All Platforms Build Convenience Script
# This script builds executables for all platforms by calling the generic build script

Write-Host "[BUILD] Building JiraUtil for All Platforms" -ForegroundColor Cyan
Write-Host "[INFO] Calling generic build script with all platforms..." -ForegroundColor Yellow

# Call the generic build script with all platforms
& .\scripts\build.ps1 -Platform all @args

if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] All platforms build completed successfully!" -ForegroundColor Green
} else {
    Write-Host "[FAIL] All platforms build failed!" -ForegroundColor Red
    exit $LASTEXITCODE
}
