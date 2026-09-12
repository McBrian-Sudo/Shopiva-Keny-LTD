from django.conf import settings
from django.http import HttpResponse
from django.urls import reverse
from django.utils import timezone

from .models import Category, Product


def _site_url():
    return getattr(settings, "PUBLIC_SITE_URL", "https://shopiva-keny-ltd.onrender.com").rstrip("/")


def robots_txt(request):
    site = _site_url()
    body = "\n".join([
        "User-agent: *",
        "Allow: /",
        "Disallow: /admin/",
        "Disallow: /account/",
        "Disallow: /cart/",
        "Disallow: /checkout/",
        "Disallow: /delivery/",
        "Disallow: /ai/",
        "Sitemap: %s/sitemap.xml" % site,
        "",
    ])
    return HttpResponse(body, content_type="text/plain; charset=utf-8")


def sitemap_xml(request):
    site = _site_url()
    urls = []

    static_names = ["home", "products", "categories", "app_install"]
    for name in static_names:
        try:
            urls.append(site + reverse(name))
        except Exception:
            continue

    for product in Product.objects.filter(is_active=True).only("id")[:50000]:
        urls.append(site + reverse("product_detail", kwargs={"product_id": product.id}))

    for category in Category.objects.all().only("id")[:50000]:
        # Categories are exposed through the main categories page; avoid guessing a detail route.
        _ = category

    lastmod = timezone.now().date().isoformat()
    xml = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for url in dict.fromkeys(urls):
        xml.append("<url><loc>%s</loc><lastmod>%s</lastmod></url>" % (url, lastmod))
    xml.append("</urlset>")
    return HttpResponse("\n".join(xml), content_type="application/xml; charset=utf-8")
