from django.http import JsonResponse
from django.views.decorators.cache import never_cache


@never_cache
def admin_session_status(request):
    """Return current admin authentication state for browser back/forward protection."""
    response = JsonResponse({
        "authenticated": bool(request.user.is_authenticated and request.user.is_staff),
    })
    response["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0, private"
    response["Pragma"] = "no-cache"
    response["Expires"] = "0"
    return response
