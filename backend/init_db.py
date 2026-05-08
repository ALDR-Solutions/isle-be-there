from sqlmodel import SQLModel

from app.infrastructure.database.engine import get_engine

# Import all models so SQLModel registers them.
from app.modules.bookings.models import Booking
from app.modules.businesses.models import Business, BusinessType
from app.modules.favourites.models import Favourites
from app.modules.interests.models import Interests, ListingInterest, UserInterest
from app.modules.listings.models import Listing
from app.modules.reviews.models import Review
from app.modules.users.models import User
from app.modules.employees.models import Business_Employee
from app.modules.itineraries.model import Itinerary, ItineraryItem
from app.modules.pricing.models import PlatformPricingConfig
from app.modules.discounts.models import Discount, DiscountType
from datetime import datetime
from sqlalchemy.orm import Session

def init_db():
    SQLModel.metadata.create_all(get_engine())

    # Seed default pricing and discounts if not present
    engine = get_engine()
    try:
        with Session(engine) as s:
            # Seed PlatformPricingConfig (global, business_type_id=None)
            if s.query(PlatformPricingConfig).first() is None:
                s.add(PlatformPricingConfig(
                    business_type_id=None,
                    service_fee_percent=0.10,
                    is_active=True,
                    effective_from=datetime.now()
                ))
            # Seed Package Discount if not present
            if s.query(Discount).filter(Discount.name == "Package Booking Discount").first() is None:
                s.add(Discount(
                    name="Package Booking Discount",
                    discount_type=DiscountType.PACKAGE,
                    discount_percent=0.05,
                    min_services=2,
                    required_business_types=["hotel", "tour"],
                    is_active=True,
                    valid_from=datetime.now()
                ))
            s.commit()
    except Exception:
        # Do not fail on seed issues; allow table creation to proceed
        pass

if __name__ == "__main__":
    init_db()
    print("Tables created ✅")
