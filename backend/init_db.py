from sqlmodel import SQLModel
from app.database.engine import get_engine

# Import all models so SQLModel registers them
from app.models.user import User
from app.models.profile import Profile
from app.models.business import Business
from app.models.business_types import BusinessType
from app.models.listing import Listing
from app.models.booking import Booking

def init_db():
    SQLModel.metadata.create_all(get_engine())

if __name__ == "__main__":
    init_db()
    print("Tables created ✅")