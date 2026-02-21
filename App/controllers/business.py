"""Utility functions for managing listings in the Supabase database.
"""
from flask import flash, render_template
from App.supabase_client import supabase
from ..controllers.auth import get_current_user
from ..forms.business import AddHotelListingForm, AddRestaurantListingForm, AddTourListingForm, AddActivityListingForm
import json


def get_current_business():
    """Retrieve the current business information from the database.

    Returns:
        dict: The current business data if found, None otherwise.
    """
    user = get_current_user()
    if not user:
        return None
    
    user_id = user.id
    try:
        response = supabase.table('businesses').select('*').eq('user_id', user_id).single().execute()
    except Exception as e:
        print("Error fetching current business:", e)
        return None

    return response.data

def get_business_listings(business_id):
    """Retrieve all listings for a specific business."""
    try:
        response = supabase.table('listings').select('*').eq('business_id', business_id).execute()
    except Exception as e:
        print("Error fetching business listings:", e)
        return []

    data = response.data or []

    # normalize/parse JSON fields returned as strings
    for item in data:
        # normalize singular image_url -> image_urls
        if 'image_url' in item and 'image_urls' not in item:
            item['image_urls'] = item.pop('image_url')

        for key in ('address', 'listing_data', 'image_urls'):
            if key in item and isinstance(item[key], str):
                try:
                    item[key] = json.loads(item[key])
                except Exception:
                    pass

    return data

def get_listing_services(listing_id):
    """Retrieve all services associated with a specific listing.

    Args:
        listing_id (int): The unique identifier of the listing.

    Returns:
        list: List of services associated with the listing.
    """
    try:
        response = supabase.table('services').select('*').eq('listing_id', listing_id).execute()
    except Exception as e:
        print("Error fetching listing services:", e)
        return []
    return response.data

def get_listing(listing_id):
    """Retrieve a single listing by id and normalize JSON fields."""
    try:
        response = supabase.table('listings').select('*').eq('id', listing_id).single().execute()
    except Exception as e:
        print("Error fetching listing:", e)
        return None

    item = response.data
    if not item:
        return None

    # normalize singular image_url -> image_urls
    if 'image_url' in item and 'image_urls' not in item:
        item['image_urls'] = item.pop('image_url')

    for key in ('address', 'listing_data', 'image_urls'):
        if key in item and isinstance(item[key], str):
            try:
                item[key] = json.loads(item[key])
            except Exception:
                pass

    return item

# Create listing functions for different business types
def create_hotel_listing(form):
    """Create a hotel listing from validated form data.
    
    Args:
        form: Validated AddHotelListingForm instance from the view
        
    Returns:
        dict: The created listing data if successful, None if an error occurs
    """
    business = get_current_business()

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

    if not business:
        print("Error: Current business not found")
        return None
    
    listings = {
        'title': form.title.data,
        'description': form.description.data,
        'address': address_data,
        'latitude': form.latitude.data,
        'longitude': form.longitude.data,
        'image_urls': [form.image_urls.data] if form.image_urls.data else None,
        'business_id': business['id'],
        'listing_data': listing_data,
    }
    
    try:
        response = supabase.table('listings').insert(listings).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print("Error creating listing:", e)
        return None
    
# def create_restaurant_listing():
#         form = AddRestaurantListingForm()
#         business = get_current_business()

#         address_data = {
#             'street': form.street.data,
#             'city': form.city.data,
#             'state': form.state.data,
#             'postal_code': form.postal_code.data,
#             'country': form.country.data,
#         }
#         listing_data = {
#             "cuisine_type": form.cuisine_type.data,
#             "seating_capacity": form.seating_capacity.data,
#             "opening_time": form.opening_time.data,
#             "closing_time": form.closing_time.data,
#             "facilites": form.facilites.data,
#             "reservation_required": form.reservation_required.data,
#             "takeout_available": form.takeout_available.data,
#             "cancellation_policy": form.cancellation_policy.data,
#             "age_requirement": form.age_requirement.data,
#             "status": form.status.data,
#         }

#         if not business:
#             flash("Failed to create restaurant listing. Please try again.", "danger")
#             return render_template("auth/add_restaurant_listing.html", form=form)
#         else:
#             listings = {
#                 'title': form.title.data,
#                 'description': form.description.data,
#                 'address': json.dumps(address_data),
#                 'latitude': form.latitude.data,
#                 'longitude': form.longitude.data,
#                 'image_urls': form.image_url.data,

#                 'business_id': business['id'],
#                 'listing_data' : json.dumps(listing_data),
#             }
#             try:
#                 response = supabase.table('listings').insert(listings).execute()
#             except Exception as e:
#                 print("Error creating listing:", e)
#                 return None
#             return response.data[0]

# def create_tour_listing():
#     form = AddTourListingForm()
#     business = get_current_business()

#     address_data = {
#         'street': form.street.data,
#         'city': form.city.data,
#         'state': form.state.data,
#         'postal_code': form.postal_code.data,
#         'country': form.country.data,
#     }
#     schedule = {
#         "schedule": form.schedule.data,
#     }
#     listing_data = {
#         "highlights": form.highlights.data,
#         "schedule": json.dumps(schedule),
#         "cancellation_policy": form.cancellation_policy.data,
#         "deposit_required": form.deposit_required.data,
#         "age_requirement": form.age_requirement.data,
#         "status": form.status.data,
#     }

#     if not business:
#         flash("Failed to create tour listing. Please try again.", "danger")
#         return render_template("auth/add_tour_listing.html", form=form)
#     else:
#         listings = {
#             'title': form.title.data,
#             'description': form.description.data,
#             'address': json.dumps(address_data),
#             'latitude': form.latitude.data,
#             'longitude': form.longitude.data,
#             'image_urls': form.image_urls.data,
#             'business_id': business['id'],
#             'listing_data' : json.dumps(listing_data),
#         }
#         try:
#             response = supabase.table('listings').insert(listings).execute()
#         except Exception as e:
#             print("Error creating listing:", e)
#             return None
#         return response.data[0]
    
# def create_activity_listing():
#     form = AddActivityListingForm()
#     business = get_current_business()

#     address_data = {
#         'street': form.street.data,
#         'city': form.city.data,
#         'state': form.state.data,
#         'postal_code': form.postal_code.data,
#         'country': form.country.data,
#     }

#     listing_data = {
#         "safety_measures": form.safety_measures.data,
#         "waiver_required": form.waiver_required.data,
#         "cancellation_policy": form.cancellation_policy.data,
#         "age_requirement": form.age_requirement.data,
#         "status": form.status.data,
#         "equipment_provided": form.equipment_provided.data,
#     }

#     if not business:
#         flash("Failed to create activity listing. Please try again.", "danger")
#         return render_template("auth/add_activity_listing.html", form=form)
#     else:
#         listings = {
#             'title': form.title.data,
#             'description': form.description.data,
#             'address': json.dumps(address_data),
#             'latitude': form.latitude.data,
#             'longitude': form.longitude.data,
#             'image_url': form.image_urls.data,
#             'business_id': business['id'],
#             'listing_data' : json.dumps(listing_data),
#         }
#         try:
#             response = supabase.table('listings').insert(listings).execute()
#         except Exception as e:
#             print("Error creating listing:", e)
#             return None
#         return response.data[0]



# def update_listing(listing_id, data):
#     """
#     Update an existing listing in the database.
#         Args:
#             listing_id: The unique identifier of the listing to update
#             data: Dictionary containing the fields to update
            
#         Returns:
#             The updated listing data if successful, None if an error occurs
            
#     Raises:
#         Prints error message if update fails
#     """
#     try:
#         response = supabase.table('listings').update(data).eq('id', listing_id).execute()
#     except Exception as e:
#         print("Error updating listing:", e)
#         return None
#     return response.data[0] if response.data else None

def update_listing(listing_id, data):
    """Update an existing listing. Returns updated record or None."""
    if not listing_id or not data:
        return None

    # try to cast listing_id to int for numeric primary keys
    try:
        lid = int(listing_id)
    except Exception:
        lid = listing_id

    # build payload and avoid setting keys to None (which would clear columns)
    payload = {}
    for k, v in data.items():
        if v is None:
            continue
        if k in ("address", "listing_data", "image_urls") and isinstance(v, (dict, list)):
            try:
                payload[k] = json.dumps(v)
            except Exception:
                payload[k] = v
        else:
            payload[k] = v

    try:
        # Perform the update. Some client versions don't support chaining .select() after update,
        # so we issue the update first and then fetch the row separately if needed.
        response = (
            supabase.table('listings')
            .update(payload)
            .eq('id', lid)
            .execute()
        )
    except Exception as e:
        print("Error updating listing (exception):", e)
        return None

    if getattr(response, "error", None):
        print("Supabase update error:", response.error)
        return None

    if getattr(response, "data", None):
        return response.data[0]

    # Fallback: some clients return empty data on update — fetch explicitly
    try:
        return get_listing(lid)
    except Exception as e:
        print("Error fetching updated listing:", e)
        return None

def delete_listing(listing_id):
    """
    Delete a listing from the database.
        Args:
            listing_id: The unique identifier of the listing to be deleted\n
        
        Returns:
            dict: The deleted listing data if successful, None if an error occurs\n
    
    Raises:
        Prints error message if deletion fails
    """
    try:
        response = supabase.table('listings').delete().eq('id', listing_id).execute()
    except Exception as e:
        print("Error deleting listing:", e)
        return None
    return response.data[0]
