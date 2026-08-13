from django.apps import AppConfig


class HomeConfig(AppConfig):
    name = "home"

    def ready(self):
        """Load the signals once the app has finished starting.

        Importing the file is enough, because the @receiver decorator
        inside it connects the function to Django.
        """
        from . import signals  # noqa: F401
