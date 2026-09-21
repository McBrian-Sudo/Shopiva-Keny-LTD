import base64
import os
import uuid
from datetime import datetime, timezone as dt_timezone

import requests
from django.core.exceptions import ImproperlyConfigured

_REDACT_KEYS = {"access_token", "refresh_token", "client_secret", "password", "authorization"}


def _env(name, default=""):
    return os.getenv(name, default).strip()


def _required(*names):
    missing = [name for name in names if not _env(name)]
    if missing:
        raise ImproperlyConfigured("Co-op Connect configuration is incomplete: " + ", ".join(missing))


def _base_url():
    return _env("COOP_CONNECT_SIT_BASE_URL", "https://openapi-sit.co-opbank.co.ke").rstrip("/")


def _safe_payload(value):
    if isinstance(value, dict):
        return {str(key): ("[REDACTED]" if str(key).lower() in _REDACT_KEYS else _safe_payload(item)) for key, item in value.items()}
    if isinstance(value, list):
        return [_safe_payload(item) for item in value]
    return value


def _request(session, method, url, **kwargs):
    kwargs.setdefault("timeout", 30)
    try:
        response = session.request(method, url, **kwargs)
        try:
            payload = response.json()
        except ValueError:
            payload = {"raw": response.text[:2000]}
        return response.status_code, payload
    except requests.RequestException as exc:
        raise RuntimeError("Co-op Connect request failed.") from exc


class CoopConnectSITClient:
    """Server-side Co-op Connect SIT connector. Secrets and access tokens stay out of the DB."""

    def __init__(self, session=None):
        self.session = session or requests.Session()

    def generate_token(self):
        _required("COOP_CONNECT_SIT_CLIENT_ID", "COOP_CONNECT_SIT_CLIENT_SECRET")
        credentials = f"{_env('COOP_CONNECT_SIT_CLIENT_ID')}:{_env('COOP_CONNECT_SIT_CLIENT_SECRET')}"
        encoded = base64.b64encode(credentials.encode("utf-8")).decode("ascii")
        status, payload = _request(
            self.session,
            "POST",
            f"{_base_url()}/token",
            headers={
                "Authorization": f"Basic {encoded}",
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json",
            },
            data={"grant_type": "client_credentials"},
        )
        token = payload.get("access_token")
        if status not in (200, 201) or not token:
            raise RuntimeError("Co-op Connect SIT authentication failed.")
        return {
            "access_token": token,
            "token_type": payload.get("token_type", "Bearer"),
            "expires_in": payload.get("expires_in"),
            "raw": _safe_payload(payload),
        }

    def stk_push(
        self,
        *,
        mobile_number,
        amount,
        callback_url,
        user_id=None,
        operator_code=None,
        message_reference=None,
        narration="SHOPIVA STK TEST",
    ):
        mobile_number = "".join(ch for ch in str(mobile_number).strip() if ch.isdigit() or ch == "+")
        if mobile_number.startswith("+254"):
            mobile_number = "254" + mobile_number[4:]
        elif mobile_number.startswith("0") and len(mobile_number) == 10:
            mobile_number = "254" + mobile_number[1:]
        elif mobile_number.startswith("7") and len(mobile_number) == 9:
            mobile_number = "254" + mobile_number
        if not mobile_number.startswith("254") or len(mobile_number) != 12:
            raise ValueError("Use a Kenyan mobile number such as 2547XXXXXXXX.")
        if not callback_url or not callback_url.lower().startswith("https://"):
            raise ValueError("Co-op Connect callback URL must use HTTPS.")

        user_id = user_id or _env("COOP_CONNECT_SIT_USER_ID")
        operator_code = operator_code or _env("COOP_CONNECT_SIT_OPERATOR_CODE")
        if not user_id or not operator_code:
            raise ImproperlyConfigured("Set COOP_CONNECT_SIT_USER_ID and COOP_CONNECT_SIT_OPERATOR_CODE.")

        try:
            amount_value = float(amount)
        except (TypeError, ValueError) as exc:
            raise ValueError("Amount must be numeric.") from exc
        if amount_value <= 0:
            raise ValueError("Amount must be greater than zero.")

        message_reference = message_reference or (
            f"SHOPIVA-SIT-{datetime.now(dt_timezone.utc):%Y%m%d%H%M%S}-{uuid.uuid4().hex[:8].upper()}"
        )
        token = self.generate_token()["access_token"]
        request_payload = {
            "MessageReference": message_reference,
            "UserId": user_id,
            "CallBackUrl": callback_url,
            "OperatorCode": operator_code,
            "TransactionCurrency": "KES",
            "MobileNumber": mobile_number,
            "Narration": (narration or "SHOPIVA STK TEST")[:120],
            "Amount": amount_value,
            "OtherDetails": [{"Name": "Source", "Value": "Shopiva SIT"}],
        }
        status, response = _request(
            self.session,
            "POST",
            f"{_base_url()}/FT/stk/1.0.0/",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            json=request_payload,
        )
        if status not in (200, 201, 202):
            raise RuntimeError("Co-op Connect SIT STK request was rejected.")
        return {"message_reference": message_reference, "http_status": status, "response": _safe_payload(response)}

    def transaction_status(self, *, message_reference, user_id=None):
        if not message_reference:
            raise ValueError("Message reference is required.")
        user_id = user_id or _env("COOP_CONNECT_SIT_USER_ID")
        if not user_id:
            raise ImproperlyConfigured("Set COOP_CONNECT_SIT_USER_ID.")
        token = self.generate_token()["access_token"]
        status, response = _request(
            self.session,
            "POST",
            f"{_base_url()}/Enquiry/STK/1.0.0/",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            json={"MessageReference": message_reference, "UserId": user_id},
        )
        if status not in (200, 201, 202):
            raise RuntimeError("Co-op Connect SIT status inquiry was rejected.")
        return {"http_status": status, "message_reference": message_reference, "response": _safe_payload(response)}


def coop_connect_sit_ready():
    return all(_env(name) for name in (
        "COOP_CONNECT_SIT_CLIENT_ID",
        "COOP_CONNECT_SIT_CLIENT_SECRET",
        "COOP_CONNECT_SIT_USER_ID",
        "COOP_CONNECT_SIT_OPERATOR_CODE",
    ))
