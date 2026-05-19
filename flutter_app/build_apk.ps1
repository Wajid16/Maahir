$ErrorActionPreference = "Stop"

Write-Host "Building Maahir AI Agentic Orchestrator for Production..." -ForegroundColor Cyan
Write-Host "Optimizing APK size using split-per-abi..." -ForegroundColor Yellow

# Clean project before building
Write-Host "Cleaning previous builds..."
C:\src\flutter\bin\flutter.bat clean
C:\src\flutter\bin\flutter.bat pub get

# Build the release APKs
Write-Host "Building APKs..."
C:\src\flutter\bin\flutter.bat build apk --release --split-per-abi

Write-Host "Build Complete!" -ForegroundColor Green
Write-Host "Your APKs are located at: build\app\outputs\flutter-apk\" -ForegroundColor Cyan
Write-Host "Use the app-armeabi-v7a-release.apk or app-arm64-v8a-release.apk for the smallest file size." -ForegroundColor Yellow
