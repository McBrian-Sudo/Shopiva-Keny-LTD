from decimal import Decimal
from xml.etree.ElementTree import Element, SubElement, tostring
from urllib.parse import urlsplit, urlunsplit

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
        url = product.image.url if product.image else ""
        if not url:
            return ""
        # Cloudinary public IDs are stored without a file extension. Google
        # Merchant Center requires an image URL whose extension matches the
        # served format, so explicitly request the WebP representation.
        parts = urlsplit(str(url))
        path = parts.path
        if not path.lower().endswith((".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".tif", ".tiff")):
            path = path.rstrip("/") + ".webp"
            url = urlunsplit((parts.scheme, parts.netloc, path, parts.query, parts.fragment))
        return url
    except Exception:
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
            # Keep the product in the feed so Merchant Center reports the exact
            # missing required image instead of silently showing zero products.
            # Do not substitute generic or invented imagery.
            image_url = ""
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
            "product_type": product.category or "General",
        }

        if product.brand:
            SubElement(item, f"{{{GOOGLE_NS}}}brand").text = product.brand
        if product.gtin:
            SubElement(item, f"{{{GOOGLE_NS}}}gtin").text = product.gtin
        if product.mpn:
            SubElement(item, f"{{{GOOGLE_NS}}}mpn").text = product.mpn
        has_identifier = bool(product.gtin or (product.brand and product.mpn))
        SubElement(item, f"{{{GOOGLE_NS}}}identifier_exists").text = "yes" if has_identifier else "no"

        for media in product.media.order_by("position")[:10]:
            try:
                extra_url = media.image.url
            except Exception:
                extra_url = ""
            if extra_url:
                SubElement(item, f"{{{GOOGLE_NS}}}additional_image_link").text = extra_url

        for tag, value in values.items():
            # image_link is required; when missing, leave it empty so Merchant
            # Center reports the missing image instead of accepting fake imagery.
            SubElement(item, f"{{{GOOGLE_NS}}}{tag}").text = value

    body = tostring(rss, encoding="utf-8", xml_declaration=True)
    return HttpResponse(body, content_type="application/xml; charset=utf-8")
