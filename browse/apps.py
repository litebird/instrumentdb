from django.apps import AppConfig


class BrowseConfig(AppConfig):
    name = "browse"

    def ready(self):
        from . import signals  # noqa: F401
