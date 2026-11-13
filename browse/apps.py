from django.apps import AppConfig


class BrowseConfig(AppConfig):
    name = "browse"

    def ready(self):
        # We import signals to register them
        import browse.signals
