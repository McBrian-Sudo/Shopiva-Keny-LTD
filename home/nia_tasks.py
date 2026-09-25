import os
import secrets

from django.core.management import call_command
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .nia_phone import _log_audit


@require_POST
def run_nia_tasks_endpoint(request):
    configured = os.getenv("NIA_CRON_SECRET", "").strip()
    supplied = request.headers.get("X-Nia-Cron-Secret", "").strip()
    if not configured or not supplied or not secrets.compare_digest(supplied, configured):
        return JsonResponse({"ok": False}, status=403)

    try:
        call_command("run_nia_tasks")
    except Exception:
        return JsonResponse({"ok": False, "error": "Nia task runner failed."}, status=500)

    _log_audit(
        request.user if getattr(request, "user", None) and request.user.is_authenticated else None,
        "admin",
        "proactive_task_runner",
        {"source": "protected_endpoint"},
    )
    return JsonResponse({"ok": True})
