# M-PESA production configuration

Shopiva uses Safaricom Daraja for customer M-PESA collection. Production merchant identifiers and credentials must come from Safaricom's approved merchant/Daraja configuration. Do not copy values from old notes, screenshots, test collections, or chat messages into production.

## Required Render variables

    MPESA_ENV=production
    MPESA_SHORTCODE=<SAFARICOM-APPROVED-BUSINESS-SHORTCODE-OR-STORE-NUMBER>
    MPESA_TILL_NUMBER=<SAFARICOM-APPROVED-TILL-NUMBER>
    MPESA_CONSUMER_KEY=<SECRET>
    MPESA_CONSUMER_SECRET=<SECRET>
    MPESA_PASSKEY=<SECRET>
    MPESA_CALLBACK_URL=https://shopivakenya.top/payments/mpesa/callback/

The current application intentionally requires both MPESA_SHORTCODE and MPESA_TILL_NUMBER in production. The code maps the shortcode to Daraja BusinessShortCode and the till number to PartyB. This mapping must match the merchant profile approved by Safaricom for the selected Buy Goods/Daraja product.

Never invent, guess, swap, or combine merchant identifiers from different Safaricom profiles.

## Credentials that must stay secret

Do not commit these values to GitHub, place them in frontend/mobile code, or paste them into chat:

- Daraja Consumer Key
- Daraja Consumer Secret
- M-PESA Passkey
- Any production certificate or signing credential

Set secrets only in the production deployment secret store.

## Callback

Use:

https://shopivakenya.top/payments/mpesa/callback/

The callback is public because Safaricom must reach it. Shopiva does not trust the callback by itself: it performs an STK query using the stored CheckoutRequestID, validates the provider identifiers, and only marks the order paid when the callback receipt, amount and phone also match the payment record.

## Go-live sequence

1. Obtain the approved production merchant identifiers and Daraja app credentials from Safaricom.
2. Put the values in Render environment variables.
3. Verify the canonical HTTPS callback above is registered with the Safaricom production app.
4. Test a real low-value production transaction with an approved test phone/account.
5. Confirm the STK callback reaches Render and that the provider query and callback metadata match.
6. Reconcile the payment record, seller settlement and inventory before opening the checkout path to customers.

Official Safaricom resources:

- https://developer.safaricom.co.ke/
- https://developer.safaricom.co.ke/apis/BusinessBuyGoods
