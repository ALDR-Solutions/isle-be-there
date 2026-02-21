# blue prints are imported 
# explicitly instead of using *
from .user import user_views
from .index import index_views
from .auth import auth_views
from .account import account_views
from .listings import listings_view
from .bookings import bookings_view
# from .admin import setup_admin


views = [user_views, index_views, auth_views, account_views, listings_view, bookings_view] 
# blueprints must be added to this list