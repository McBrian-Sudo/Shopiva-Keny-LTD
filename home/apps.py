from django.apps import AppConfig


class HomeConfig(AppConfig):
    name = "home"

    def ready(self):
        # Register product-media signals without changing existing marketplace flows.
        from . import media_signals  # noqa: F401
