#!/usr/bin/env bash
set -euo pipefail

ANDROID_SDK_ROOT="${ANDROID_SDK_ROOT:-$HOME/Android/Sdk}"
export ANDROID_SDK_ROOT
export ANDROID_HOME="$ANDROID_SDK_ROOT"

if ! command -v java >/dev/null 2>&1; then
  echo "Java is required. Install Java 17 first."
  exit 1
fi

JAVA_VERSION="$(java -version 2>&1 | head -1)"
echo "Detected: $JAVA_VERSION"

echo "Android SDK root: $ANDROID_SDK_ROOT"

if ! command -v sdkmanager >/dev/null 2>&1; then
  echo "sdkmanager was not found on PATH. Install Android SDK Command-line Tools and add its cmdline-tools/latest/bin directory to PATH."
  exit 1
fi

sdkmanager --licenses < /dev/null || true
sdkmanager "platform-tools" "platforms;android-36" "build-tools;36.0.0"

if command -v gradle >/dev/null 2>&1; then
  gradle --version
  echo "Building Shopiva Delivery debug APK..."
  (cd "$(dirname "$0")/../delivery-android" && gradle :app:assembleDebug)
else
  echo "Gradle was not found. Install Gradle 9.5.0 or use Android Studio's Gradle integration."
fi
