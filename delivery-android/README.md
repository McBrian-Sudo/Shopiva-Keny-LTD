# Shopiva Admin Android

The single native Android administration client for Shopiva Kenya LTD.

## What it does

- Opens the production Shopiva Admin Control Center.
- Uses the same Django staff/admin authentication and permissions as the web Admin Control Center.
- Gives authorized staff mobile access to the same Shopiva control surface already implemented on the main platform: products, orders, users, commercial intelligence, delivery command/map tools, categories and operational actions.
- Is not a customer shopping app and is not intended for Google Play, Apple App Store or other public app marketplaces.
- The customer shopping experience remains the main Shopiva application and will be prepared for official store distribution.

## Security model

The APK contains no admin password and does not grant privileges by itself. The production Django server remains the authority. A customer account cannot become an administrator merely by installing, copying or modifying the APK because `/admin/` is protected server-side.

The signed Admin APK must be distributed privately to authorized Shopiva staff. Do not publish the Admin APK or AAB to public releases, Google Play, Apple App Store, or other public download stores.

## Android target

The project targets Android 16 / API 36 and compiles against API 36. Google Play requires new apps and updates submitted from August 31, 2026 to target API 36 or higher.

## Build

Open the `delivery-android` folder in Android Studio or use GitHub Actions. Production signing is enabled only when the Shopiva signing secrets are present. Never commit the keystore, passwords or signing keys to the repository.

## Production endpoint

The production Shopiva URL is configured in `app/src/main/java/ke/co/shopiva/admin/ShopivaConfig.java` and the application opens `/admin/`.
