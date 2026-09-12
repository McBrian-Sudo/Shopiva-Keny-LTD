import json
from html import escape
from urllib.parse import urljoin

from django.conf import settings
from django.utils.html import strip_tags


def _site_url():
    return getattr(settings, "PUBLIC_SITE_URL", "https://shopiva-keny-ltd.onrender.com").rstrip("/")


def _absolute_image(product):
    try:
        url = product.image.url
    except Exception:
        return ""
    return urljoin(_site_url() + "/", url.lstrip("/"))


class ShopivaSeoMiddleware:
    """Adds crawl-friendly metadata without requiring every template to share a base file."""

    PRIVATE_PREFIXES = (
        "/admin/",
        "/account/",
        "/cart/",
        "/checkout/",
        "/delivery/",
        "/seller/",
        "/customer/",
        "/ai/",
        "/payments/",
        "/health/",
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        path = request.path or "/"

        if any(path == prefix.rstrip("/") or path.startswith(prefix) for prefix in self.PRIVATE_PREFIXES):
            response["X-Robots-Tag"] = "noindex, nofollow"
            return response

        if response.get("Content-Type", "").lower().split(";", 1)[0].strip() != "text/html":
            return response
        if getattr(response, "streaming", False):
            return response

        try:
            html = response.content.decode(response.charset or "utf-8")
        except Exception:
            return response

        site = _site_url()
        canonical = urljoin(site + "/", path.lstrip("/"))
        title = "Shopiva Kenya | Smart Shopping Marketplace"
        description = (
            "Shopiva Kenya is a smart online marketplace for shopping, products, sellers, secure ordering, "
            "M-PESA payments and delivery across Kenya."
        )
        image = ""
        schema = None

        if path.startswith("/product/"):
            try:
                product_id = int(path.rstrip("/").split("/")[-1])
                from .models import Product

                product = Product.objects.filter(id=product_id, is_active=True).first()
                if product:
                    title = f"{product.name} | Shopiva Kenya"
                    raw_description = strip_tags(product.description or "").strip()
                    description = raw_description[:155] or f"Shop {product.name} on Shopiva Kenya."
                    image = _absolute_image(product)
                    schema = {
                        "@context": "https://schema.org",
                        "@type": "Product",
                        "name": product.name,
                        "description": raw_description or description,
                        "url": canonical,
                        "brand": {"@type": "Brand", "name": "Shopiva"},
                        "offers": {
                            "@type": "Offer",
                            "url": canonical,
                            "priceCurrency": "KES",
                            "price": f"{product.discounted_price:.2f}",
                            "availability": (
                                "https://schema.org/InStock"
                                if product.stock_quantity > 0
                                else "https://schema.org/OutOfStock"
                            ),
                        },
                    }
                    if image:
                        schema["image"] = [image]
            except Exception:
                schema = None
        else:
            schema = {
                "@context": "https://schema.org",
                "@type": "OnlineStore",
                "name": "Shopiva Kenya",
                "alternateName": "Shopiva Kenya LTD",
                "url": site + "/",
                "description": description,
                "areaServed": "KE",
            }

        page_type = "product" if path.startswith("/product/") else "website"
        tags = [
            f'<link rel="canonical" href="{escape(canonical, quote=True)}">',
            f'<meta name="description" content="{escape(description, quote=True)}">',
            '<meta name="robots" content="index, follow, max-image-preview:large">',
            f'<meta property="og:type" content="{page_type}">',
            '<meta property="og:site_name" content="Shopiva Kenya">',
            f'<meta property="og:title" content="{escape(title, quote=True)}">',
            f'<meta property="og:description" content="{escape(description, quote=True)}">',
            f'<meta property="og:url" content="{escape(canonical, quote=True)}">',
            '<meta name="twitter:card" content="summary_large_image">',
            f'<meta name="twitter:title" content="{escape(title, quote=True)}">',
            f'<meta name="twitter:description" content="{escape(description, quote=True)}">',
        ]
        if image:
            tags.extend([
                f'<meta property="og:image" content="{escape(image, quote=True)}">',
                f'<meta name="twitter:image" content="{escape(image, quote=True)}">',
            ])
        if schema:
            tags.append(
                '<script type="application/ld+json">%s</script>'
                % json.dumps(schema, ensure_ascii=False, separators=(",", ":"))
            )

        injection = "\n".join(tags)
        marker = "</head>"
        lower_html = html.lower()
        index = lower_html.find(marker)
        if index >= 0:
            html = html[:index] + injection + "\n" + html[index:]
            encoded = html.encode(response.charset or "utf-8")
            response.content = encoded
            response["Content-Length"] = str(len(encoded))
        return response
