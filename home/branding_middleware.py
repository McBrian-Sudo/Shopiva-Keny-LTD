from django.db import connection
from django.http import HttpResponse
from django.templatetags.static import static


class ShopivaBrandingMiddleware:
    """Apply the active customer-app brand stored in PostgreSQL to HTML responses."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        content_type = response.get("Content-Type", "")
        if "text/html" not in content_type or not response.content:
            return response

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT logo_path FROM home_shopivabranding "
                    "WHERE app_code = %s AND is_active = TRUE LIMIT 1",
                    ["customer"],
                )
                row = cursor.fetchone()
            logo_path = row[0] if row else "branding/shopiva-shopping-logo.svg"
        except Exception:
            logo_path = "branding/shopiva-shopping-logo.svg"

        logo_url = static(logo_path)
        body = response.content.decode(response.charset or "utf-8")

        old_logo = '<a href="/" class="logo">\\n            Shopiva<span>Kenya</span>\\n        </a>'
        new_logo = (
            '<a href="/" class="logo shopiva-brand-link" aria-label="Shopiva Kenya LTD home">'
            f'<img src="{logo_url}" alt="Shopiva Kenya LTD" class="shopiva-brand-logo">'
            '</a>'
        )
        body = body.replace(old_logo, new_logo)

        if "shopiva-branding-css" not in body:
            branding_css = (
                '<style id="shopiva-branding-css">'
                '.shopiva-brand-link{display:flex!important;align-items:center;gap:8px;height:52px;}'
                '.shopiva-brand-logo{width:52px;height:52px;display:block;object-fit:contain;border-radius:14px;}'
                '.shopiva-brand-link:hover{transform:translateY(-1px);}'
                '</style>'
            )
            body = body.replace("</head>", branding_css + "</head>", 1)

        if 'rel="icon"' not in body and "rel='icon'" not in body:
            body = body.replace(
                "</head>",
                f'<link rel="icon" type="image/svg+xml" href="{logo_url}">'
                f'<link rel="apple-touch-icon" href="{logo_url}"></head>',
                1,
            )

        new_response = HttpResponse(body, status=response.status_code, reason=response.reason, content_type=content_type)
        for key, value in response.items():
            if key.lower() not in {"content-length", "content-type"}:
                new_response[key] = value
        return new_response
