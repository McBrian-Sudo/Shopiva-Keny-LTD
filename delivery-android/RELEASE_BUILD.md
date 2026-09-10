# Shopiva Delivery Android — Build & Signing

## Local build requirements

- Java 17
- Android SDK with API 36 platform and build tools
- Gradle 9.5.0 or the Android Studio Gradle integration

From the repository root:

```bash
cd delivery-android
gradle :app:assembleDebug
gradle :app:assembleRelease
gradle :app:bundleRelease
```

The release build is intentionally unsigned unless the signing environment variables are present.

## Production signing

Never commit a keystore, passwords, or signing keys to GitHub.

Set these environment variables locally or in GitHub Actions:

```text
SHOPIVA_ANDROID_KEYSTORE_PATH
SHOPIVA_ANDROID_STORE_PASSWORD
SHOPIVA_ANDROID_KEY_ALIAS
SHOPIVA_ANDROID_KEY_PASSWORD
```

For GitHub Actions, also create these repository secrets:

```text
SHOPIVA_ANDROID_KEYSTORE_BASE64
SHOPIVA_ANDROID_KEYSTORE_PASSWORD
SHOPIVA_ANDROID_KEY_ALIAS
SHOPIVA_ANDROID_KEY_PASSWORD
```

The workflow automatically creates a signed APK and AAB when all signing secrets are present. Without them, it still produces debug and unsigned release artifacts for testing.

## Create a production keystore

Run this once on a trusted machine:

```bash
keytool -genkeypair -v \
  -keystore shopiva-delivery-release.jks \
  -alias shopiva-delivery \
  -keyalg RSA -keysize 4096 \
  -validity 10000
```

Back up the `.jks` file and passwords securely. Losing the production signing key can prevent future releases from updating the same Android application.

## Convert the keystore for GitHub Actions

Linux/macOS:

```bash
base64 -w 0 shopiva-delivery-release.jks > shopiva-release-keystore.base64
```

Windows PowerShell:

```powershell
[Convert]::ToBase64String([IO.File]::ReadAllBytes("shopiva-delivery-release.jks")) | Set-Content shopiva-release-keystore.base64
```

Copy the resulting Base64 text into the GitHub Actions secret `SHOPIVA_ANDROID_KEYSTORE_BASE64`.

## What to distribute

- **APK**: direct installation/testing on Android phones.
- **AAB**: preferred upload format for Google Play publishing.
- **Shopiva Market**: PWA for customers across Android, iOS, Windows, macOS, Linux and ChromeOS.
