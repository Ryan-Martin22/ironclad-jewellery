"""Checkout App"""
from django.apps import AppConfig


class CheckoutConfig(AppConfig):
    """Checkout configuration class"""
    name = 'checkout'

    # Overrides ready method and imports signals module
    def ready(self):
        import checkout.signals
