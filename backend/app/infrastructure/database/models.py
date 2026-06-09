"""Import all SQLModel model modules so relationship targets are registered."""

from app.modules.availability import models as availability_models
from app.modules.bookings import models as bookings_models
from app.modules.businesses import models as businesses_models
from app.modules.discounts import models as discounts_models
from app.modules.employees import models as employees_models
from app.modules.favourites import models as favourites_models
from app.modules.interests import models as interests_models
from app.modules.itineraries import models as itineraries_models
from app.modules.listings import models as listings_models
from app.modules.pricing import models as pricing_models
from app.modules.reviews import models as reviews_models
from app.modules.services import models as services_models
from app.modules.stripe_payment import models as stripe_payment_models
from app.modules.users import models as users_models

__all__ = [
    "availability_models",
    "bookings_models",
    "businesses_models",
    "discounts_models",
    "employees_models",
    "favourites_models",
    "interests_models",
    "itineraries_models",
    "listings_models",
    "pricing_models",
    "reviews_models",
    "services_models",
    "stripe_payment_models",
    "users_models",
]
