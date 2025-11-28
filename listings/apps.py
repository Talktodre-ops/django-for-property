from django.apps import AppConfig


class ListingsConfig(AppConfig):
    """Configuration for the listings application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "listings"
    verbose_name = "Property Listings"

