# Shopiva Delivery Location Data Notice

Shopiva Delivery collects a delivery partner's device location only when the partner has enabled delivery tracking.

Location is used to:

- support active delivery operations;
- update the assigned order's delivery status and map;
- provide the customer with delivery progress and location information related to their order;
- maintain operational delivery history for safety, support and dispute resolution.

The Android app runs a visible location foreground service while tracking is enabled and shows a persistent notification. The rider can stop tracking at any time.

Location data is transmitted to the Shopiva server over HTTPS and is associated with the authorized delivery-partner account.

## Retention

Delivery GPS history is retained for up to 90 days for operational safety, support and dispute resolution, unless a longer period is required for an active legal, fraud, payment or customer-support investigation. Older location pings can be removed with the server-side prune_delivery_locations management command.

Current location is exposed only through authenticated Shopiva delivery/customer/admin workflows scoped to the relevant order or staff role. The public storefront does not expose delivery location history.

Shopiva should keep its published privacy notice aligned with this retention schedule before wider app-store distribution.

The current implementation intentionally does not request Android's ACCESS_BACKGROUND_LOCATION permission. Continuous updates while the app is in the background are provided through an Android location foreground service started by the rider from the visible app. This reduces unnecessary permission scope while preserving the delivery-tracking use case.
