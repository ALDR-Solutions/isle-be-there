from stripe import Stripe as StripeClient
from .config import settings

stripe = StripeClient(settings.STRIPE_SECRET_KEY) if settings.STRIPE_SECRET_KEY else None

__all__ = ["stripe"]