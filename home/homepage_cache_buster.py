class ShopivaHomepageCacheBusterMiddleware:
    """Keep the public Shopiva homepage fresh without rewriting its HTML or assets."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.path == "/":
            response["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0, s-maxage=0"
            response["Pragma"] = "no-cache"
            response["Expires"] = "0"
            response["X-Shopiva-Homepage-Version"] = "2026-09-15-real-category-images-v2"
        return response
