from sqlmodel import SQLModel

from app.infrastructure.database.engine import get_engine

# Import all models so SQLModel registers them.
from app.modules.bookings.models import Booking
from app.modules.businesses.models import Business, BusinessType
from app.modules.favourites.models import Favourites
from app.modules.interests.models import Interests, ListingInterest, UserInterest
from app.modules.listings.models import Listing
from app.modules.reviews.models import Review
from app.modules.users.models import Profile, User

def init_db():
    SQLModel.metadata.create_all(get_engine())

if __name__ == "__main__":
    init_db()
    print("Tables created ✅")
