class ShopivaHomepageCacheBusterMiddleware:
    """Prevent stale cached HTML and suppress the obsolete Shopping homepage top banner."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.path == "/":
            response["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0, s-maxage=0"
            response["Pragma"] = "no-cache"
            response["Expires"] = "0"
            response["X-Shopiva-Homepage-Version"] = "2026-09-15-marketplace-carousel-no-topbar"
            if response.get("Content-Type", "").startswith("text/html"):
                obsolete_banner = (
                    b'<div class="topbar"><div class="wrap topbar-in">'
                    b'\xf0\x9f\x87\xb0\xf0\x9f\x87\xaa <strong>Shopiva Kenya LTD</strong> \xc2\xb7 Smart shopping built for Kenya'
                    b'<div class="toplinks"><span>Verified sellers</span><span>Tracked delivery</span><span>Secure checkout</span></div>'
                    b'</div></div>'
                )
                response.content = response.content.replace(obsolete_banner, b"")
                response["Content-Length"] = str(len(response.content))
        return response
