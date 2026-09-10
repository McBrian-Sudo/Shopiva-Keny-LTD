# Shopiva Admin Android

The single native Android administration client for Shopiva Kenya LTD.

## What it does

- Opens the production Shopiva Admin Control Center.
- Uses the same Django staff/admin authentication and permissions as the web Admin Control Center.
- Gives authorized staff access to the Shopiva management dashboard and the controls already implemented on the main platform, including products, orders, users, commercial intelligence, delivery command/map tools, categories and operational actions.
- Is not a customer shopping app and is not intended for Google Play or the Apple App Store.
- Customer access is still handled by the main Shopiva shopping site/PWA and its planned official store distribution.

## Security model

The APK itself is not the authority for admin access. The production Django server remains the authority. A customer account cannot gain staff access by installing or modifying the APK because `/admin/` is protected server-side.

For distribution, the Admin APK is produced as a signed workflow artifact instead of a public customer-facing store release. Do not publish the Admin APK to Google Play, Apple App Store or other public app marketplaces.

## Build

Open the `delivery-android` folder in Android Studio. The project uses Java 17, compile SDK 36, target SDK 36 and Gradle 9.5 through GitHub Actions.

The GitHub Actions workflow at `.github/workflows/delivery-android-build.yml` builds debug and release outputs. Production signing is enabled only when the GitHub repository signing secrets are present.

## Production endpoint

The production Shopiva URL is configured in `app/src/main/java/ke/co/shopiva/delivery/ShopivaConfig.java` and the application opens `/admin/`.
