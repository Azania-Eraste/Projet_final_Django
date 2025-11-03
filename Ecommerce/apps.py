from django.apps import AppConfig


class EcommerceConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "Ecommerce"

    def ready(self):
        # Import signals to ensure they're registered
        try:
            from . import signals  # noqa: F401
        except Exception:
            pass
