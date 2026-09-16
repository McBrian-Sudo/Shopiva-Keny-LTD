import re
from django.http import HttpResponse

# Approved Shopiva bicycle-hub photo supplied by the project owner.
# Embedded so the hero has no external-image dependency and cannot show a broken image.
BICYCLE_HUB_IMAGE = "data:image/webp;base64,UklGRqCAAABXRUJQVlA4IJSAAADwlwGdASqsAT0BPj0ci0QiIaETqUY0IAPEsrRpaPFu0Z+uARRWQ6F1vHTW6rT6v9evovxv8ZWJj1H/V8w3nX/hf4f8evlr/1PXL+tf957hP7F/sB2B/3f9UP7Y/tp7q//P/ar3n/tf+yP+w+Qv+lf2n/3e1t/yvZ7/wH/D9hb9qP//6837gfET/ZP+j+3HtYf/TC0OZX8fwP/Kfrf9t/hv3b/yvuPYe+wzUR+ifkb+L/ivaP/W97/zE/6PUF/M/69/x/nU+iX73tgNm/5PoF++v4X/t/5n1B/v//h6R/sH+2/8v3VfYF/Pf7Z/yvY7/teIv6j7Af9R/x//v/1P5Q/TT/q//nzwfYf/09xH+i/4z/zcC1+9TLVqdrPMmPpcONnnuostUyv1kwSJJEpY0MaVT7am/12pNZ+rPC/7Kwj6uUsWFQ+ucvsN2IMuhiKjeX+RhxONhFAKvCwU6fzORdFGU5E3Z61iSmIdal/1yCT4Ny9X89QwVkwlrMku0S8gsqFD+qfnJqOpSVmL/wYy+luLce9n47GwMFqsF/YGtkYRiaX1j21ZwaphezkIAK0VstTHWFhhbPbEFgiLrXycdIK8+bLoBCyhodwugv+RmMzktOzSH9kN5F+RAenRsnscOm20lq65RZJDszSIiLQISlH6CPOjvvJlCaD0K8jkD/++QePiocEVCl0rTkk0Su1SJeR0IfGO9mv8I7fHbdthKimpYSiiXmEKcw2lTf0IHLwxMrherv3e3S3aN4xoN+vqtGN5Lc91clb+fsbBLNJcNgvr36XbDFmpvinSUsO4ZzGk6sZt+Avh2ZLlWtjO94SLf9/DujP8aY0aCD+1pPVjQts8BTgtPORWOHvCnVf7V2hHnnZUXwrmT+dV6Z7fR76u9vrdXDUYS7i/06jB4bTOu14Qss+gsOVTo6OZLvcsbr92oALjKOK9iPGK04qt/dpaYBY7TIakxo5mDdzMWARmEc4kZtLHtPaalnJTYIiMLhyh4N1Dsnio1yXF5tUBdRDNj3TGiK50pQOO8P4oZs9Oz7JGLCNJVFZqmThvUSaxZCrAPkiM2NkZSGj7RJ6f"

BICYCLE_CSS = r"""
<style id="shopiva-bicycle-hero-css">
.shopiva-bicycle-hero{position:relative;height:500px;margin:15px 0 22px;border-radius:24px;overflow:hidden;background:#071b31;color:#fff;box-shadow:0 18px 50px rgba(6,26,47,.10);isolation:isolate}
.shopiva-bicycle-hero-media{position:absolute;inset:0;z-index:0}
.shopiva-bicycle-hero-media img{width:100%;height:100%;display:block;object-fit:cover;object-position:center center}
.shopiva-bicycle-hero-shade{position:absolute;inset:0;z-index:1;background:linear-gradient(90deg,rgba(3,12,25,.76) 0%,rgba(4,19,37,.52) 34%,rgba(4,19,37,.18) 62%,rgba(4,19,37,.04) 100%)}
.shopiva-bicycle-hero-content{position:relative;z-index:2;height:100%;display:flex;flex-direction:column;justify-content:center;max-width:760px;padding:48px 52px 70px}
.shopiva-bicycle-eyebrow{display:inline-flex;align-items:center;width:max-content;padding:8px 12px;border-radius:999px;border:1px solid rgba(255,255,255,.22);background:rgba(255,255,255,.09);font-size:10px;font-weight:1000;letter-spacing:.14em}
.shopiva-bicycle-hero h1{font-size:clamp(38px,5.4vw,74px);line-height:.92;letter-spacing:-.07em;margin:18px 0 16px}
.shopiva-bicycle-hero h1 strong{color:#19d978;font-weight:1000}
.shopiva-bicycle-hero p{max-width:620px;color:rgba(255,255,255,.86);font-size:15px;line-height:1.65}
.shopiva-bicycle-actions{display:flex;flex-wrap:wrap;gap:10px;margin-top:24px}
.shopiva-bicycle-btn{display:inline-flex;align-items:center;justify-content:center;padding:13px 17px;border-radius:11px;font-size:10px;font-weight:1000}
.shopiva-bicycle-btn-primary{background:#fff;color:#061a2f}
.shopiva-bicycle-btn-secondary{border:1px solid rgba(255,255,255,.28);background:rgba(255,255,255,.08);color:#fff}
@media(max-width:760px){.shopiva-bicycle-hero{height:430px}.shopiva-bicycle-hero-media img{object-position:58% center}.shopiva-bicycle-hero-content{padding:34px 24px 52px;max-width:90%}.shopiva-bicycle-hero h1{font-size:clamp(34px,11vw,54px)}.shopiva-bicycle-hero p{font-size:13px}}
</style>
"""

BICYCLE_HERO = r"""
<section class="shopiva-bicycle-hero" aria-label="Shopiva Bicycle Spares">
  <div class="shopiva-bicycle-hero-media"><img src="__IMAGE__" alt="Shopiva bicycle hubs and spare parts"></div>
  <div class="shopiva-bicycle-hero-shade"></div>
  <div class="shopiva-bicycle-hero-content">
    <span class="shopiva-bicycle-eyebrow">SHOPIVA · BICYCLE SPARES</span>
    <h1>Bicycle Hubs &amp;<br><strong>Spare Parts</strong></h1>
    <p>Quality hubs and bicycle components for repairs, upgrades and custom builds.</p>
    <div class="shopiva-bicycle-actions">
      <a href="/products/?q=bicycle" class="shopiva-bicycle-btn shopiva-bicycle-btn-primary">Shop Bicycle Spares →</a>
      <a href="/categories/" class="shopiva-bicycle-btn shopiva-bicycle-btn-secondary">Browse Categories</a>
    </div>
  </div>
</section>
""".replace("__IMAGE__", BICYCLE_HUB_IMAGE)

def _replace_first_element_by_class(html, tag_name, class_name, replacement):
    tag_rx = re.compile(r"<%s\\b[^>]*>" % re.escape(tag_name), re.IGNORECASE)
    class_rx = re.compile(r"class\\s*=\\s*['\\\"]([^'\\\"]*)['\\\"]", re.IGNORECASE)
    opening = None
    for match in tag_rx.finditer(html):
        classes = class_rx.search(match.group(0))
        if classes and re.search(r"\\b%s\\b" % re.escape(class_name), classes.group(1), re.IGNORECASE):
            opening = match
            break
    if not opening:
        return html, False
    token_rx = re.compile(r"<(/?)([A-Za-z][\\w:-]*)\\b[^>]*>", re.IGNORECASE)
    depth = 1
    for token in token_rx.finditer(html, opening.end()):
        if token.group(2).lower() != tag_name.lower():
            continue
        if token.group(1):
            depth -= 1
            if depth == 0:
                return html[:opening.start()] + replacement + html[token.end():], True
        elif not token.group(0).rstrip().endswith("/>"):
            depth += 1
    return html, False

class ShopivaBrandingMiddleware:
    """Use only the approved bicycle-hub photo as the public homepage hero."""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        content_type = response.get("Content-Type", "")
        if request.path != "/" or "text/html" not in content_type or not response.content:
            return response
        html = response.content.decode("utf-8", errors="replace")
        html = re.sub(r"(?is)<style[^>]*id=['\"]shopiva-bicycle-hero-css['\"][^>]*>.*?</style>", "", html)
        html, _ = _replace_first_element_by_class(html, "section", "shopiva-bicycle-hero", "")
        html = re.sub(r"(?is)<div[^>]*class=['\"][^'\"]*\bshopiva-bike-v2\b[^'\"]*['\"][^>]*>.*?</div>\s*</div>", "", html)
        html, replaced = _replace_first_element_by_class(html, "div", "hero", BICYCLE_CSS + BICYCLE_HERO)
        if not replaced:
            marker = re.search(r"(?is)(<div[^>]*class=['\"][^'\"]*\bquick\b[^'\"]*['\"][^>]*>)", html)
            if marker:
                html = html[:marker.start()] + BICYCLE_CSS + BICYCLE_HERO + html[marker.start():]
            else:
                html = html.replace("</body>", BICYCLE_CSS + BICYCLE_HERO + "</body>", 1)
        response = HttpResponse(html, status=response.status_code, content_type=response.get("Content-Type", "text/html"))
        response["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response["Pragma"] = "no-cache"
        response["Expires"] = "0"
        response["X-Shopiva-Bicycle-Hero"] = "approved-hub-image-v2"
        return response
