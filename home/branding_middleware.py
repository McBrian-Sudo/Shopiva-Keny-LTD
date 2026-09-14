from django.http import HttpResponse


class ShopivaBrandingMiddleware:
    """Apply only non-destructive legacy branding outside the shopping homepage."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        content_type = response.get("Content-Type", "")
        if "text/html" not in content_type or not response.content:
            return response

        # The public Shopping homepage owns its complete visual system.
        # Never inject, replace, or mutate its logo/navigation/graphics.
        if request.path == "/":
            return response

        return response
