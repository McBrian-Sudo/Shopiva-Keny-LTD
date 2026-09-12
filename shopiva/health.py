from django.db import connection
from django.http import JsonResponse


def health(request):
    """Minimal unauthenticated liveness/readiness probe for production monitoring."""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except Exception:
        return JsonResponse({"status": "unhealthy"}, status=503)

    return JsonResponse({"status": "ok"}, status=200)
