import json

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render

from .coop_connect import CoopConnectSITClient, coop_connect_sit_ready


@staff_member_required(login_url="/admin/login/")
def coop_connect_sit_console(request):
    result = None
    error = None

    if request.method == "POST":
        action = request.POST.get("action", "").strip()
        try:
            client = CoopConnectSITClient()
            if action == "token":
                data = client.generate_token()
                result = {
                    "operation": "OAuth token generation",
                    "status": "success",
                    "details": {
                        "token_type": data.get("token_type"),
                        "expires_in": data.get("expires_in"),
                        "response": data.get("raw"),
                    },
                }
                messages.success(request, "Co-op Connect SIT authentication succeeded.")
            elif action == "stk":
                result = {
                    "operation": "STK Push",
                    "status": "success",
                    "details": client.stk_push(
                        mobile_number=request.POST.get("mobile_number", ""),
                        amount=request.POST.get("amount", ""),
                        callback_url=request.POST.get("callback_url", "").strip(),
                        message_reference=request.POST.get("message_reference", "").strip() or None,
                        narration=request.POST.get("narration", "").strip() or "SHOPIVA STK TEST",
                    ),
                }
                messages.success(request, "Co-op Connect SIT STK request was accepted.")
            elif action == "status":
                result = {
                    "operation": "STK Transaction Status",
                    "status": "success",
                    "details": client.transaction_status(
                        message_reference=request.POST.get("message_reference", "").strip(),
                    ),
                }
                messages.success(request, "Co-op Connect SIT status inquiry completed.")
            else:
                error = "Unknown SIT action."
        except Exception as exc:
            error = str(exc)

    return render(
        request,
        "admin/coop_connect_sit.html",
        {
            "ready": coop_connect_sit_ready(),
            "result": json.dumps(result, indent=2, default=str) if result else "",
            "error": error,
            "default_callback": request.POST.get("callback_url", ""),
            "default_mobile": request.POST.get("mobile_number", ""),
            "default_amount": request.POST.get("amount", "1"),
            "default_reference": request.POST.get("message_reference", ""),
            "default_narration": request.POST.get("narration", "SHOPIVA STK TEST"),
        },
    )
