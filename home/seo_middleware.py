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

    PUBLIC_PREFIXES = ("/", "/products/", "/categories/", "/product/", "/install/")
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
        if any(path == prefix.rstrip("/") or path.startswith(prefix) for prefix in self.PRIVATE_PREFIXES if prefix != "/"):
            response["X-Robots-Tag"] = "noindex, nofollow"
            return response

        content_type = response.get("Content-Type", "")
        if "text/html" not in content_type.lower() or not getattr(response, "streaming", False) is False:
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
                    product_schema = {
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
                            "price": str(product.discounted_price.quantize(product.price.as_tuple()._replace(exponent=-2).exponent and 0.01)),
                            "availability": "https://schema.org/InStock" if product.stock_quantity > 0 else "https://schema.org/OutOfStock",
                        },
                    }
                    if image:
                        product_schema["image"] = [image]
                    schema = product_schema
                else:
                    schema = None
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

        tags = [
            f'<link rel="canonical" href="{escape(canonical, quote=True)}">',
            f'<meta name="description" content="{escape(description, quote=True)}">',
            '<meta name="robots" content="index, follow, max-image-preview:large">',
            f'<meta property="og:type" content="{"product" if path.startswith("/product/") else "website"}">',
            f'<meta property="og:site_name" content="Shopiva Kenya">',
            f'<meta property="og:title" content="{escape(title, quote=True)}">',
            f'<meta property="og:description" content="{escape(description, quote=True)}">',
            f'<meta property="og:url" content="{escape(canonical, quote=True)}">',
            f'<meta name="twitter:card" content="summary_large_image">',
            f'<meta name="twitter:title" content="{escape(title, quote=True)}">',
            f'<meta name="twitter:description" content="{escape(description, quote=True)}">',
        ]
        if image:
            tags.extend([
                f'<meta property="og:image" content="{escape(image, quote=True)}">',
                f'<meta name="twitter:image" content="{escape(image, quote=True)}">',
            ])
        if schema:
            tags.append('<script type="application/ld+json">%s</script>' % json.dumps(schema, ensure_ascii=False))

        injection = "\n".join(tags)
        if "</head>" in html.lower():
            idx = html.lower().find("</head>")
            html = html[:idx] + injection + "\n" + html[idx:]
            response.content = html.encode(response.charset or "utf-8")
            response["Content-Length"] = str(len(response.content))
        return response
