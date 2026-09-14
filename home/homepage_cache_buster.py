import re


class ShopivaHomepageCacheBusterMiddleware:
    """Keep the live Shopping homepage fresh and apply storefront presentation fixes."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.path == "/":
            response["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0, s-maxage=0"
            response["Pragma"] = "no-cache"
            response["Expires"] = "0"
            response["X-Shopiva-Homepage-Version"] = "2026-09-15-marketplace-carousel-light"

            if response.get("Content-Type", "").startswith("text/html"):
                # Remove the thin legacy announcement strip completely from the HTML.
                response.content = re.sub(
                    rb'<div class="topbar">.*?</div>\s*</div>\s*<header class="nav">',
                    b'<header class="nav">',
                    response.content,
                    count=1,
                    flags=re.DOTALL,
                )

                # Reduce the heavy navy overlay so product photography remains bright.
                response.content = response.content.replace(
                    b'linear-gradient(90deg,rgba(3,12,25,.95) 0%,rgba(4,19,37,.86) 35%,rgba(4,19,37,.22) 63%,rgba(4,19,37,.12) 100%)',
                    b'linear-gradient(90deg,rgba(3,12,25,.48) 0%,rgba(4,19,37,.30) 35%,rgba(4,19,37,.08) 63%,rgba(4,19,37,.03) 100%)',
                )
                response["Content-Length"] = str(len(response.content))
        return response
