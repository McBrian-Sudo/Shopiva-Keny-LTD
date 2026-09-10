# Shopiva M-PESA production configuration

Shopiva uses Safaricom Daraja for M-PESA payment requests and payment verification.

## Merchant details supplied by Shopiva

- M-PESA Buy Goods Till Number: `1692454`
- Safaricom/merchant Store Number: `1221718`
- Current operator ID: `MN`
- Desired business/operator display name: `Shopiva Kenya LTD`

## Important distinction

The Till Number and Store Number are merchant-side identifiers. The operator ID/display name is controlled by the Safaricom M-PESA business/Daraja account and should not be hard-coded into the Django application as a secret. Renaming the operator from `MN` to `Shopiva Kenya LTD` must be completed in the relevant Safaricom business account/admin tooling or by Safaricom support if the portal does not allow the change.

## Credentials that must stay secret

Do **not** commit these values to GitHub and do not paste them into chat:

- Daraja Consumer Key
- Daraja Consumer Secret
- M-PESA Passkey (where required by the selected Daraja product)
- Any production certificate or signing credential

Set secrets as Render environment variables instead.

Recommended variable names:

```text
MPESA_ENV=production
MPESA_TILL_NUMBER=1692454
MPESA_STORE_NUMBER=1221718
MPESA_OPERATOR_ID=MN
MPESA_OPERATOR_NAME=Shopiva Kenya LTD
MPESA_CONSUMER_KEY=
MPESA_CONSUMER_SECRET=
MPESA_PASSKEY=
MPESA_CALLBACK_URL=https://shopiva-keny-ltd.onrender.com/payments/mpesa/callback/
```

The application must verify the Daraja callback before marking an order as paid. It must never treat the customer's browser redirect or a submitted form as proof of payment.

## Daraja

Use the official Safaricom Daraja developer portal for the API application, sandbox testing, production credentials and go-live process:
https://developer.safaricom.co.ke/

The production callback URL must be public HTTPS and must point to the deployed Shopiva service.
