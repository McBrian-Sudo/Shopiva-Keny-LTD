from decimal import Decimal
from xml.etree.ElementTree import Element, SubElement, tostring

from django.conf import settings
from django.http import HttpResponse
from django.utils.html import strip_tags

from .models import Product


GOOGLE_NS = "http://base.google.com/ns/1.0"


def _site_url():
    return str(
        getattr(settings, "PUBLIC_SITE_URL", "https://shopivakenya.top")
        or "https://shopivakenya.top"
    ).rstrip("/")


def _image_url(product):
    try:
        if product.image and product.image.url:
            return product.image.url
    except Exception:
        pass
    return ""


def merchant_feed_xml(request):
    """Generate a Google Merchant product feed from active listings with real images."""
    site = _site_url()

    rss = Element("rss", {
        "version": "2.0",
        "xmlns:g": GOOGLE_NS,
    })
    channel = SubElement(rss, "channel")
    SubElement(channel, "title").text = "Shopiva Kenya"
    SubElement(channel, "link").text = site + "/"
    SubElement(channel, "description").text = (
        "Shopiva Kenya online marketplace product catalogue."
    )

    products = (
        Product.objects.filter(is_active=True)
        .select_related("seller")
        .order_by("-id")[:50000]
    )

    for product in products:
        image_url = _image_url(product)
        if not image_url:
            # Merchant listings should use a real representative product image.
            continue

        item = SubElement(channel, "item")
        price = product.discounted_price.quantize(Decimal("0.01"))
        description = strip_tags(product.description or "").strip()
        if not description:
            description = f"Shop {product.name} on Shopiva Kenya."

        values = {
            "id": str(product.sku or f"shopiva-{product.id}"),
            "title": product.name,
            "description": description[:5000],
            "link": f"{site}/product/{product.id}/",
            "image_link": image_url,
            "price": f"{price:.2f} KES",
            "availability": "in_stock" if product.stock_quantity > 0 else "out_of_stock",
            "condition": "new",
            "identifier_exists": "false",
            "product_type": product.category or "General",
        }

        for tag, value in values.items():
            SubElement(item, f"{{{GOOGLE_NS}}}{tag}").text = value

    body = tostring(rss, encoding="utf-8", xml_declaration=True)
    return HttpResponse(body, content_type="application/xml; charset=utf-8")
