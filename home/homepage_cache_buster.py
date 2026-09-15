import re


class ShopivaHomepageCacheBusterMiddleware:
    """Keep the live Shopping homepage fresh and apply storefront presentation fixes."""

    CATEGORY_POSITIONS = (
        ("c1", "0%"),
        ("c2", "9.0909%"),
        ("c3", "18.1818%"),
        ("c4", "27.2727%"),
        ("c5", "36.3636%"),
        ("c6", "45.4545%"),
        ("c7", "54.5455%"),
        ("c8", "63.6364%"),
        ("c9", "72.7273%"),
        ("c10", "81.8182%"),
        ("c11", "90.9091%"),
        ("c12", "100%"),
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.path == "/":
            response["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0, s-maxage=0"
            response["Pragma"] = "no-cache"
            response["Expires"] = "0"
            response["X-Shopiva-Homepage-Version"] = "2026-09-15-real-category-photography"

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

                # Replace the emoji category icons with the generated real-product photo sprite.
                for css_class, position in self.CATEGORY_POSITIONS:
                    pattern = rf'<div class="cat-icon {re.escape(css_class)}">.*?</div>'
                    replacement = (
                        f'<div class="cat-icon {css_class}" '
                        f'style="background-image:url(https://raw.githubusercontent.com/McBrian-Sudo/Shopiva-Keny-LTD/main/home/static/shopiva/category-images/category-sprite.webp);'
                        f'background-size:1200% 100%;background-position:{position} 50%;'
                        f'background-repeat:no-repeat;background-color:#f2f5f7;font-size:0;">'
                        f'</div>'
                    ).encode("utf-8")
                    response.content = re.sub(pattern.encode("utf-8"), replacement, response.content, count=1)

                # Make category photo tiles taller and premium-looking while remaining responsive.
                response.content = response.content.replace(
                    b'.cat-icon{width:45px;height:45px;border-radius:13px;margin:0 auto 7px;display:grid;place-items:center;font-size:21px}',
                    b'.cat-icon{width:100%;height:118px;border-radius:0;margin:0;display:block;background-size:1200% 100%;background-repeat:no-repeat;background-color:#f2f5f7;font-size:0}',
                )
                response.content = response.content.replace(
                    b'.cat b{font-size:8px}',
                    b'.cat b{font-size:9px}',
                )
                response.content = response.content.replace(
                    b'.cat small{display:block;color:#7b8790;font-size:7px;margin-top:2px}',
                    b'.cat small{display:block;color:#7b8790;font-size:7px;margin-top:2px}',
                )
                response.content = response.content.replace(
                    b'.cat{background:#fff;border:1px solid var(--line);border-radius:14px;padding:11px 5px;text-align:center;transition:.2s}',
                    b'.cat{background:#fff;border:1px solid var(--line);border-radius:14px;overflow:hidden;padding:0 0 10px;text-align:center;transition:.2s}',
                )
                response.content = response.content.replace(
                    b'.cat:hover{transform:translateY(-3px);box-shadow:0 14px 28px rgba(6,26,47,.08)}',
                    b'.cat:hover{transform:translateY(-3px);box-shadow:0 14px 28px rgba(6,26,47,.12)}',
                )
                response.content = response.content.replace(
                    b'@media(max-width:760px){.wrap{width:min(100% - 18px,560px)}',
                    b'@media(max-width:760px){.cat-icon{height:118px}.wrap{width:min(100% - 18px,560px)}',
                )
                response.content = response.content.replace(
                    b'@media(max-width:430px){.copy h1{font-size:43px}',
                    b'@media(max-width:430px){.cat-icon{height:105px}.copy h1{font-size:43px}',
                )
                response["Content-Length"] = str(len(response.content))
        return response
