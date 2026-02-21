from flask import redirect, render_template, request, url_for, Blueprint, flash
from ..controllers.decorators import role_required
from ..controllers.business import get_business_listings, get_current_business, create_hotel_listing, get_listing, update_listing
from ..forms.business import AddHotelListingForm, AddRestaurantListingForm, AddTourListingForm, AddActivityListingForm, EditHotelListingForm

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

@business_view.route('/listings')
@role_required("business")
def listings():
    """Display all listings for the current business."""
    business = get_current_business()
    if not business:
        flash("Business not found.", "danger")
        return redirect(url_for('business.index'))
    
    business_listings = get_business_listings(business['id'])
    return render_template('business/business_listings.html', listings=business_listings, business=business)


@business_view.route('/listings/add', methods=['GET', 'POST'])
@role_required("business")
def add_listing():
    """Add a new listing (hotel, restaurant, tour, or activity)."""
    form = AddHotelListingForm()
    
    if form.validate_on_submit():
        try:
            listing = create_hotel_listing(form)
            if listing:
                flash(f"Hotel listing '{form.title.data}' created successfully!", "success")
                return redirect(url_for('business.listings'))
            else:
                flash("Failed to create hotel listing. Please try again.", "danger")
        except Exception as e:
            flash(f"Error creating listing: {str(e)}", "danger")
    
    return render_template('business/add_listing.html', form=form)

@business_view.route('/listings/<listing_id>/edit', methods=['GET', 'POST'])
@role_required("business")
def edit_listing(listing_id):
    """Edit a hotel listing (GET shows form, POST updates)."""
    listing = get_listing(listing_id)
    if not listing:
        flash("Listing not found.", "danger")
        return redirect(url_for('business.listings'))

    form = EditHotelListingForm()
    # populate form from listing
    form.title.data = listing.get('title', '')
    form.description.data = listing.get('description', '')
    addr = listing.get('address') or {}
    form.street.data = addr.get('street', '')
    form.city.data = addr.get('city', '')
    form.state.data = addr.get('state', '')
    form.country.data = addr.get('country', '')
    form.postal_code.data = addr.get('postal_code', '')
    form.latitude.data = listing.get('latitude', '')
    form.longitude.data = listing.get('longitude', '')
    imgs = listing.get('image_urls') or []
    form.image_url.data = imgs[0] if isinstance(imgs, list) and imgs else ''

    ld = listing.get('listing_data') or {}
    form.star_rating.data = str(ld.get('star_rating', '1'))
    form.hotel_type.data = ld.get('hotel_type', '')
    form.room_count.data = ld.get('room_count', '')
    form.available_rooms.data = ld.get('available_rooms', '')
    form.amenities.data = ', '.join(ld.get('amenities', [])) if isinstance(ld.get('amenities', []), list) else ld.get('amenities', '')
    form.nearby_attractions.data = ', '.join(ld.get('nearby_attractions', [])) if isinstance(ld.get('nearby_attractions', []), list) else ld.get('nearby_attractions', '')
    form.age_requirement.data = ld.get('age_requirement', '')
    form.deposit_required.data = ld.get('deposit_required', False)
    form.cancellation_policy.data = ld.get('cancellation_policy', '')
    form.status.data = ld.get('status', False)
    form.last_renovation_date.data = ld.get('last_renovation_date', '')

    if form.validate_on_submit():
        address_data = {
            'street': form.street.data,
            'city': form.city.data,
            'state': form.state.data,
            'postal_code': form.postal_code.data,
            'country': form.country.data,
        }
        listing_data = {
            "hotel_type": form.hotel_type.data,
            "room_count": form.room_count.data,
            "amenities": [item.strip() for item in form.amenities.data.split(',')] if form.amenities.data else [],
            "available_rooms": form.available_rooms.data,
            "nearby_attractions": [item.strip() for item in form.nearby_attractions.data.split(',')] if form.nearby_attractions.data else [],
            "cancellation_policy": form.cancellation_policy.data,
            "deposit_required": form.deposit_required.data,
            "age_requirement": form.age_requirement.data,
            "status": form.status.data,
            "last_renovation_date": form.last_renovation_date.data,
            'star_rating': form.star_rating.data,
        }

        update_data = {
            'title': form.title.data,
            'description': form.description.data,
            'address': address_data,
            'latitude': form.latitude.data,
            'longitude': form.longitude.data,
            'image_urls': [form.image_url.data] if form.image_url.data else None,
            'listing_data': listing_data,
        }

        updated = update_listing(listing_id, update_data)
        if updated:
            flash("Listing updated successfully.", "success")
            return redirect(url_for('business.listings'))
        else:
            flash("Failed to update listing. Check server logs.", "danger")

    return render_template('business/edit_listing.html', form=form, listing=listing)

