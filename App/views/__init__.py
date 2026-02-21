# blue prints are imported 
# explicitly instead of using *
from .user import user_views
from .index import index_views
from .auth import auth_views
from .account import account_views
from .listings import listings_view
from .bookings import bookings_view
from .business import business_view
# from .admin import setup_admin


views = [user_views, index_views, auth_views, account_views, listings_view, bookings_view, business_view]  # add new blueprints here
# blueprints must be added to this list