from django.http import HttpResponse


class ShopivaBrandingMiddleware:
    """Keep storefront branding additive and never inject a fragile logo image."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        content_type = response.get("Content-Type", "")
        if "text/html" not in content_type or not response.content:
            return response

        body = response.content.decode(response.charset or "utf-8")

        # The Shopping homepage now owns its complete branding and navigation.
        # Do not replace its brand markup or inject an external/static <img>.
        # That prevents broken-logo graphics and avoids altering existing UI.
        if request.path == "/":
            branding_css = (
                '<style id="shopiva-branding-css">'
                '.shopiva-seller-link{display:inline-flex!important;align-items:center;gap:6px;'
                'padding:10px 12px;border-radius:12px;background:#e7fff0!important;color:#087642!important;'
                'border:1px solid #c7ead5;font-weight:900!important;white-space:nowrap;}'
                '.shopiva-seller-link:hover{background:#d7f8e5!important;transform:translateY(-1px);}'
                '</style>'
            )
            if "shopiva-branding-css" not in body and "</head>" in body:
                body = body.replace("</head>", branding_css + "</head>", 1)

            # Keep the seller call-to-action available even if an older cached
            # homepage template reaches production.
            if "href=\"/seller/register/\"" not in body and "href='/seller/register/'" not in body:
                seller_link = '<a class="shopiva-seller-link" href="/seller/register/">🏪 Sell on Shopiva</a>'
                nav_match = __import__("re").search(r'(<nav\s+class=["\']links["\'][^>]*>)', body, flags=__import__("re").I)
                if nav_match:
                    at = nav_match.end()
                    body = body[:at] + seller_link + body[at:]

        new_response = HttpResponse(
            body,
            status=response.status_code,
            reason=getattr(response, "reason", None),
            content_type=content_type,
        )
        for key, value in response.items():
            if key.lower() not in {"content-length", "content-type"}:
                new_response[key] = value
        return new_response
