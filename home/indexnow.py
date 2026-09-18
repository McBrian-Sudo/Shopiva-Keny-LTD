import logging

import requests
from django.conf import settings
from django.http import HttpResponse

logger = logging.getLogger(__name__)


def _key():
    return str(getattr(settings, "INDEXNOW_KEY", "") or "").strip()


def _site():
    return str(
        getattr(settings, "PUBLIC_SITE_URL", "https://shopivakenya.top")
        or "https://shopivakenya.top"
    ).rstrip("/")


def indexnow_key(request, key):
    """Serve the IndexNow verification key at the site root."""
    expected = _key()
    if not expected or key != expected:
        return HttpResponse("Not Found", status=404, content_type="text/plain")
    return HttpResponse(expected, content_type="text/plain; charset=utf-8")


def submit_urls(urls):
    """Best-effort notification of URL changes to IndexNow."""
    key = _key()
    if not key:
        return False

    unique_urls = []
    seen = set()
    for url in urls or []:
        value = str(url or "").strip()
        if value and value.startswith(_site() + "/") and value not in seen:
            seen.add(value)
            unique_urls.append(value)

    if not unique_urls:
        return False

    endpoint = "https://api.indexnow.org/indexnow"
    payload = {
        "host": _site().replace("https://", "").replace("http://", ""),
        "key": key,
        "keyLocation": f"{_site()}/{key}.txt",
        "urlList": unique_urls[:10000],
    }
    try:
        response = requests.post(endpoint, json=payload, timeout=5)
        if response.status_code in (200, 202):
            logger.info("IndexNow submitted %s URL(s)", len(unique_urls))
            return True
        logger.warning("IndexNow submission returned status=%s body=%s", response.status_code, response.text[:300])
    except requests.RequestException as exc:
        logger.warning("IndexNow submission failed: %s", exc)
    return False
