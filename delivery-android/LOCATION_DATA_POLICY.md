# Shopiva Delivery Location Data Notice

Shopiva Delivery collects a delivery partner's device location only when the partner has enabled delivery tracking.

Location is used to:

- support active delivery operations;
- update the assigned order's delivery status and map;
- provide the customer with delivery progress and location information related to their order;
- maintain operational delivery history for safety, support and dispute resolution.

The Android app runs a visible location foreground service while tracking is enabled and shows a persistent notification. The rider can stop tracking at any time.

Location data is transmitted to the Shopiva server over HTTPS and is associated with the authorized delivery-partner account. Shopiva should publish a complete privacy policy and retention schedule before Google Play release.

The current implementation intentionally does not request Android's `ACCESS_BACKGROUND_LOCATION` permission. Continuous updates while the app is in the background are provided through an Android location foreground service started by the rider from the visible app. This reduces unnecessary permission scope while preserving the delivery-tracking use case.
