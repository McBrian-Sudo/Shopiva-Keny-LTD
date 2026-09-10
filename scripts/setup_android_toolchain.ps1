$ErrorActionPreference = "Stop"

if (-not (Get-Command java -ErrorAction SilentlyContinue)) {
    Write-Host "Java 17 is required. Install a JDK first."
    exit 1
}

java -version

if (-not (Get-Command sdkmanager -ErrorAction SilentlyContinue)) {
    Write-Host "sdkmanager was not found on PATH. Install Android SDK Command-line Tools and add cmdline-tools/latest/bin to PATH."
    exit 1
}

sdkmanager --licenses
sdkmanager "platform-tools" "platforms;android-36" "build-tools;36.0.0"

if (Get-Command gradle -ErrorAction SilentlyContinue) {
    gradle --version
    Push-Location "$PSScriptRoot\..\delivery-android"
    gradle :app:assembleDebug
    Pop-Location
} else {
    Write-Host "Gradle 9.5.0 was not found. Install Gradle or use Android Studio's Gradle integration."
}
