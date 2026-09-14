import re

from django.http import HttpResponse
from django.templatetags.static import static


class ShopivaBrandingMiddleware:
    """Apply Shopiva storefront branding without changing customer functionality."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        content_type = response.get("Content-Type", "")
        if "text/html" not in content_type or not response.content:
            return response

        body = response.content.decode(response.charset or "utf-8")
        logo_path = "shopiva/shopiva-shopping-logo.svg"

        # Prefer the active database brand when available, but never make
        # branding capable of breaking the storefront if the table is absent
        # or temporarily unavailable.
        try:
            from django.db import connection

            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT logo_path FROM home_shopivabranding "
                    "WHERE app_code = %s AND is_active = TRUE LIMIT 1",
                    ["customer"],
                )
                row = cursor.fetchone()
            if row and row[0]:
                logo_path = row[0]
        except Exception:
            pass

        logo_url = static(logo_path)
        logo_markup = (
            '<a href="/" class="logo shopiva-brand-link" aria-label="Shopiva Kenya LTD home">'
            f'<img src="{logo_url}" alt="Shopiva Kenya LTD" class="shopiva-brand-logo">'
            '</a>'
        )

        # Replace the legacy text-only logo regardless of whitespace/indentation.
        body = re.sub(
            r'<a\s+href=["\']/["\']\s+class=["\']logo["\'][^>]*>[\s\S]*?</a>',
            logo_markup,
            body,
            count=1,
            flags=re.I,
        )

        branding_css = (
            '<style id="shopiva-branding-css">'
            '.shopiva-brand-link{display:flex!important;align-items:center;gap:9px;height:56px;}'
            '.shopiva-brand-logo{width:56px;height:56px;display:block;object-fit:contain;border-radius:15px;}'
            '.shopiva-brand-link:hover{transform:translateY(-1px);}'
            '.shopiva-seller-link{display:inline-flex!important;align-items:center;gap:6px;padding:10px 13px;'
            'border-radius:10px;background:#effaf4!important;color:#087448!important;border:1px solid #ccebdd;'
            'font-weight:800!important;white-space:nowrap;}'
            '.shopiva-seller-link:hover{background:#e0f6e9!important;}'
            '@media(max-width:900px){.shopiva-brand-logo{width:48px;height:48px;}.shopiva-brand-link{height:48px;}}'
            '</style>'
        )
        if "shopiva-branding-css" not in body and "</head>" in body:
            body = body.replace("</head>", branding_css + "</head>", 1)

        # The public storefront keeps the seller CTA visible without removing
        # any existing customer navigation. Add it only once on the homepage.
        if request.path == "/" and "shopiva-seller-link" not in body:
            seller_link = '<a class="shopiva-seller-link" href="/seller/register/">🏪 Sell on Shopiva</a>'
            nav_match = re.search(r'(<div\s+class=["\']nav-links["\'][^>]*>)', body, flags=re.I)
            if nav_match:
                insert_at = nav_match.end()
                body = body[:insert_at] + seller_link + body[insert_at:]

        if 'rel="icon"' not in body and "rel='icon'" not in body and "</head>" in body:
            body = body.replace(
                "</head>",
                f'<link rel="icon" type="image/svg+xml" href="{logo_url}">'
                f'<link rel="apple-touch-icon" href="{logo_url}"></head>',
                1,
            )

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
