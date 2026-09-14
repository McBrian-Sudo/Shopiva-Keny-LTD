# Shopiva Kenya — Google Play release pack

## Public app
- App: Shopiva Kenya
- Package: ke.co.shopiva.customer
- Version: 1.1.0
- Version code: 2
- Target SDK: 36 (Android 16)
- Public distribution: YES
- Admin/Delivery: NO

## Store description
Shopiva Kenya brings everyday shopping closer to you. Discover products from local sellers, compare prices, add items to your cart, choose delivery details, place orders and track your purchases from one simple marketplace.

### Key features
- Product search and categories
- Product details, prices, stock and promotions
- Cart and checkout
- Delivery addresses and location support
- Order history and tracking
- Wishlist and reviews
- Seller marketplace
- Secure account access
- Kenya-focused shopping experience

## Payment disclosure
During the Safaricom production onboarding period, M-PESA production checkout is deliberately gated and must not be advertised as active. Only payment methods actually enabled in production should be shown to customers.

## Privacy
Privacy policy: https://shopiva-keny-ltd.onrender.com/privacy/
Account deletion: https://shopiva-keny-ltd.onrender.com/account/delete/
Terms: https://shopiva-keny-ltd.onrender.com/terms/

## Release artifact
The CI release gate produces:
- app-release.aab — upload this signed bundle to Play Console
- app-release-unsigned.apk — testing/inspection only

The CI-generated release is intentionally unsigned. Final Play distribution must use the developer's Play App Signing/upload-key configuration.

## Required Play Console work
1. Create the Shopiva Kenya application in Play Console.
2. Complete developer account verification and app access requirements.
3. Upload the signed AAB from CI.
4. Complete App content declarations, Data safety, Content rating and target audience.
5. Add privacy-policy URL and account-deletion URL.
6. Add screenshots, app icon, feature graphic and store listing.
7. Start internal testing.
8. Verify install, login, catalogue, cart, checkout, order creation and support flows.
9. Promote the verified release to production.

## Important
Do not publish Admin or Delivery packages as public apps. They are private operational applications.
