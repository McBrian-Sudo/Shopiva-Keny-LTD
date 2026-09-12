# Shopiva Google Maps Production Setup

Shopiva now uses Google Maps JavaScript API, Places API (New) / Places Library, and AdvancedMarkerElement for seller pickup, customer delivery addresses, checkout location capture and delivery tracking.

## Google Cloud project

1. Open Google Cloud Console and create/select the Shopiva project.
2. Attach a billing account. Google requires billing for production Maps JavaScript usage.
3. Enable **Maps JavaScript API**.
4. Enable **Places API (New)**. Places Autocomplete uses the Places Library.
5. Create a **JavaScript map ID**. The code has a `DEMO_MAP_ID` fallback for testing, but production should use the Shopiva map ID.
6. Create a browser API key. Do not commit it to GitHub.

## Browser key restrictions

Application restriction: **Websites (HTTP referrers)**.

Authorized referrer:

`https://shopiva-keny-ltd.onrender.com/*`

API restrictions: allow only the APIs used by the browser key:

- Maps JavaScript API
- Places API
- Places API (New)

Do not use this browser key for server-to-server web services. Create a separate IP-restricted server key whenever a Google web service is added to the Django backend.

## Render environment

Set these variables on the `Shopiva-Keny-LTD` service:

`GOOGLE_MAPS_API_KEY=<browser key>`

`GOOGLE_MAPS_MAP_ID=<production JavaScript map ID>`

Never paste either secret/credential into a repository file. The browser API key is public at runtime, so its security comes from application and API restrictions.

## Shopiva behaviour

- Seller product listing requires a pickup/business address plus latitude and longitude.
- Customer saved delivery addresses require a map pin.
- Delivery partners can share live browser GPS only while the delivery workspace is active.
- Customer tracking endpoints expose delivery coordinates only for the signed-in customer's own orders.
- Admin delivery mapping consumes the protected rider-location endpoint.

## Important

The map cannot be made live by code alone without a valid Google Cloud project, billing, enabled APIs, a restricted browser key and a production map ID. Once those two Render variables are populated, refresh the seller Add Product page and the Google map/search controls will initialize.
