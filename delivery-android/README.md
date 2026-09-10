# Shopiva Delivery Android

Native Android companion for Shopiva delivery partners. It keeps a foreground location service running while delivery tracking is enabled and sends location updates to the Shopiva server.

## Important

The delivery partner must explicitly sign in and enable tracking. Android shows a persistent notification while the location foreground service is active. The application does not silently track users.

The Shopiva server endpoint is configured in `app/src/main/java/ke/co/shopiva/delivery/ShopivaConfig.java`.
