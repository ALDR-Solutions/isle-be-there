from flask import redirect, render_template, request, url_for, Blueprint
from ..controllers.decorators import role_required
from ..controllers.business import get_business_listings

business_view = Blueprint('business', __name__, template_folder='../templates/business', url_prefix='/business')

@business_view.route('/')
@role_required("business")
def index():
    """Render the business home page."""
    # business = get_current_business()
    # if not business:
    #      return redirect(url_for('business.setup'))
    # business_id = business['id']
    # business_name = business.get('business_name', business.get('name', 'Business'))
    
    # listings = get_business_listings(business_id)
    
    #Code for Danny to CODE
    # total_bookings = calculate_total_bookings(business_id)
    # profile_views = calculate_profile_views(business_id)
    # average_rating = calculate_average_rating(business_id)
    # total_revenue = calculate_total_revenue(business_id)
    
    # recent_bookings = get_recent_bookings(business_id)
    # return render_template('business/home.html',
    #                      business_name=business_name,
    #                      total_bookings=total_bookings,
    #                      profile_views=profile_views,
    #                      average_rating=average_rating,
    #                      total_revenue=total_revenue,
    #                      recent_bookings=recent_bookings)
    
    return render_template('business/home.html')

@business_view.route('/listings/<int:listing_id>/edit', methods=['GET', 'POST'])
def add_listing(listing_id):
    if request.method == 'POST':
        # Process the form submission and add the listing
        return redirect(url_for('business.index'))

