"""
WSGI config for shopiva project.

It exposes the WSGI callable as a module-level variable named application.

For more information on this file, see
https://docs.djangoproject.com/en/6.1/howto/deployment/wsgi/
"""

import logging
import os

from django.core.management import call_command
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "shopiva.settings")

application = get_wsgi_application()

# Render's current build command runs migrations but does not explicitly run
# collectstatic. Build the WhiteNoise static bundle once when the web process
# starts so production assets are available even after a fresh deploy.
try:
    call_command("collectstatic", interactive=False, verbosity=0, clear=False)
except Exception:
    logging.getLogger(__name__).exception("Shopiva production collectstatic failed")
