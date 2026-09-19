# Shopiva Internal Android Apps

Shopiva Kenya LTD maintains two Android applications for private operational use:

- **Shopiva Admin** (delivery-android) — internal control-center application.
- **Shopiva Delivery** (delivery-driver-android) — internal delivery-partner application.

These two applications are **not intended for publication to Google Play, the Apple App Store, or any public app marketplace**.

## Distribution model

The GitHub release workflow builds internal artifacts only. It does not contain a store-publishing step for the Admin or Delivery applications.

Each internal Android job uploads:
- a debug APK for direct internal testing;
- an unsigned release APK;
- a release AAB for controlled future signing/distribution.

Production release signing keys must never be committed to this repository. Store-specific credentials, keystores, passwords, and signing certificates must remain in a protected secret-management system.

Access to the Admin and Delivery applications should be limited to authorized Shopiva personnel and controlled devices. Removing an employee or delivery partner must include revoking account access and, where applicable, device access.

The public customer application remains separate from these internal applications.
