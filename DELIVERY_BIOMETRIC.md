# Shopiva Delivery Biometric Security

Shopiva Delivery uses Android's secure biometric system for private delivery-partner devices.

## Account lifecycle

Delivery-partner accounts are provisioned and activated by Shopiva operations/admin staff. A delivery worker does not become an authorized delivery partner merely by creating a public marketplace account.

The first time an authorized delivery worker signs in to the Delivery app with their Shopiva credentials, the app offers biometric enrollment. On supported devices, a strong facial biometric can be used; Android may present another enrolled strong biometric when face is not available.

## What Shopiva stores

Shopiva does **not** upload or store a face photograph, facial template, raw biometric scan, or other biometric image in the Django/Neon database.

Instead, Android creates a device-bound cryptographic key inside Android Keystore. The private key is protected by the device's strong biometric subsystem and is not exposed to the Shopiva server or WebView.

The biometric therefore acts as a local gate for the Delivery app rather than as a server-side face-recognition database.

## Login behavior

After biometric enrollment:
1. The Delivery app starts with a biometric verification gate.
2. Successful verification unlocks the Delivery workspace and its existing authenticated Shopiva session.
3. A delivery worker can choose **Use password** when biometric verification is unavailable or cancelled.
4. If the device loses its valid biometric key, the worker must authenticate with the Shopiva password and can enroll again.

## Security purpose

The biometric gate reduces the chance that an unattended delivery phone can be opened and used to view or operate assigned orders. It is defense in depth and does not replace:
- Shopiva account passwords;
- active DeliveryAgent authorization;
- order-to-rider assignment checks;
- delivery handover-code verification;
- GPS/assignment controls;
- HTTPS/session/CSRF protections.

No internet application can honestly be guaranteed impossible to compromise, so Shopiva uses multiple independent controls rather than treating biometrics as a single security boundary.

## Privacy

Because the biometric is handled by Android and the private key remains in the device keystore, Shopiva's backend does not receive the worker's facial image or biometric template. This is intentional: storing biometric images centrally would create a more sensitive breach target.

