# Shopiva Delivery Android

Native Android companion for Shopiva delivery partners.

## What it does

- Opens the production Shopiva delivery workspace inside the app.
- Lets the delivery partner explicitly start and stop tracking.
- Runs a visible Android location foreground service while tracking is active.
- Sends GPS latitude, longitude, accuracy, speed and heading to Shopiva over HTTPS.
- Continues location updates while the app is minimized or the screen is locked, subject to Android device and battery-management rules.
- Uses the existing authenticated Shopiva delivery session, so customer/admin credentials are not exposed by the location service.

## Permissions

The app requests precise/coarse location and notifications. It does not request `ACCESS_BACKGROUND_LOCATION`; ongoing background operation is provided by the user-started location foreground service. Android requires an appropriate foreground-service location declaration and permission for modern target SDKs. See `LOCATION_DATA_POLICY.md` for the privacy disclosure.

## Build

Open the `delivery-android` folder in Android Studio. The project uses Android Gradle Plugin 9.3.0, Gradle 9.5, Java 17, compile SDK 36, target SDK 36, and `com.google.android.gms:play-services-location:21.4.0`.

A GitHub Actions workflow at `.github/workflows/delivery-android-build.yml` builds the debug APK on changes to this project.

## Production endpoint

The server endpoint is configured in `app/src/main/java/ke/co/shopiva/delivery/ShopivaConfig.java`.
