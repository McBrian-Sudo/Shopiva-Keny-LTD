import re
from django.http import HttpResponse


def _strip_brand_images(html):
    """Remove legacy logo <img> and visual fallback elements from the header brand block."""
    tag_rx = re.compile(r"<([A-Za-z][\\w:-]*)\\b[^>]*>", re.IGNORECASE)
    class_rx = re.compile(r"class\\s*=\\s*['\"]([^'\"]*)['\"]", re.IGNORECASE)
    opening = None
    tag_name = None
    for match in tag_rx.finditer(html):
        classes = class_rx.search(match.group(0))
        if classes and re.search(r"\\bbrand\\b", classes.group(1), re.IGNORECASE):
            opening = match
            tag_name = match.group(1).lower()
            break
    if not opening:
        return html, False

    token_rx = re.compile(r"<(/?)([A-Za-z][\\w:-]*)\\b[^>]*>", re.IGNORECASE)
    depth = 1
    end = None
    closing = ""
    for token in token_rx.finditer(html, opening.end()):
        if token.group(2).lower() != tag_name:
            continue
        if token.group(1):
            depth -= 1
            if depth == 0:
                end = token.end()
                closing = token.group(0)
                break
        elif not token.group(0).rstrip().endswith("/>"):
            depth += 1
    if end is None:
        return html, False

    block_end = end - len(closing)
    block = html[opening.end():block_end]
    cleaned = re.sub(r"(?is)<img\\b[^>]*>\\s*", "", block)
    cleaned = re.sub(r"(?is)<[^>]*\\bbrand-fallback\\b[^>]*>.*?</[^>]+>\\s*", "", cleaned)
    if cleaned == block:
        return html, False
    return html[:opening.end()] + cleaned + html[block_end:], True


class ShopivaBrandingMiddleware:
    """Final public-home cleanup only; never injects or replaces homepage hero content."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        content_type = response.get("Content-Type", "")
        if request.path != "/" or "text/html" not in content_type or not response.content:
            return response

        html = response.content.decode("utf-8", errors="replace")
        html, _ = _strip_brand_images(html)

        response = HttpResponse(
            html,
            status=response.status_code,
            content_type=response.get("Content-Type", "text/html"),
        )
        response["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response["Pragma"] = "no-cache"
        response["Expires"] = "0"
        response["X-Shopiva-Brand-Cleanup"] = "header-image-free-v1"
        return response
