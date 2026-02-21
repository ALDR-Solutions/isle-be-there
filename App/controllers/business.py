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
    """Retrieve all listings for a specific business.

    Args:
        business_id (int): The unique identifier of the business.
    Returns:
        list: List of listings associated with the business.
    """ 
    try:
        response = supabase.table('listings').select('*').eq('business_id', business_id).execute()
    except Exception as e:
        print("Error fetching business listings:", e)
        return []
    return response.data

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


# Create listing functions for different business types
def create_hotel_listing():
    form = AddHotelListingForm()
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
        "facilities": form.facilities.data,
		"amenities": form.amenities.data,
		"available_rooms": form.available_rooms.data,
		"nearby_attractions": form.nearby_attractions.data,
		"cancellation_policy": form.cancellation_policy.data,
		"deposit_required": form.deposit_required.data,
		"age_requirement": form.age_requirement.data,
		"status": form.status.data,
        "last_renovation_date": form.last_renovation_date.data,
        'star_rating': form.star_rating.data,
    }

    if not business:
        flash("Failed to create hotel listing. Please try again.", "danger")
        return render_template("auth/add_hotel_listing.html", form=form)
    else:
        listings = {
            'title': form.title.data,
            'description': form.description.data,
            'address': json.dumps(address_data),
            'lattitude': form.lattitude.data,
            'longitude': form.longitude.data,
            'image_url': form.image_url.data,
            'business_type': 'hotel',
            'business_id': business['id'],
            'listing_data' : json.dumps(listing_data),
        }
        try:
            response = supabase.table('listings').insert(listings).execute()
        except Exception as e:
            print("Error creating listing:", e)
            return None
        return response.data[0]
    
def create_restaurant_listing():
        form = AddRestaurantListingForm()
        business = get_current_business()

        address_data = {
            'street': form.street.data,
            'city': form.city.data,
            'state': form.state.data,
            'postal_code': form.postal_code.data,
            'country': form.country.data,
        }
        listing_data = {
            "cuisine_type": form.cuisine_type.data,
            "seating_capacity": form.seating_capacity.data,
            "opening_time": form.opening_time.data,
            "closing_time": form.closing_time.data,
            "facilites": form.facilites.data,
            "reservation_required": form.reservation_required.data,
            "takeout_available": form.takeout_available.data,
            "cancellation_policy": form.cancellation_policy.data,
            "age_requirement": form.age_requirement.data,
            "status": form.status.data,
        }

        if not business:
            flash("Failed to create restaurant listing. Please try again.", "danger")
            return render_template("auth/add_restaurant_listing.html", form=form)
        else:
            listings = {
                'title': form.title.data,
                'description': form.description.data,
                'address': json.dumps(address_data),
                'lattitude': form.lattitude.data,
                'longitude': form.longitude.data,
                'image_url': form.image_url.data,
                'business_type': 'hotel',
                'business_id': business['id'],
                'listing_data' : json.dumps(listing_data),
            }
            try:
                response = supabase.table('listings').insert(listings).execute()
            except Exception as e:
                print("Error creating listing:", e)
                return None
            return response.data[0]

def create_tour_listing():
    form = AddTourListingForm()
    business = get_current_business()

    address_data = {
        'street': form.street.data,
        'city': form.city.data,
        'state': form.state.data,
        'postal_code': form.postal_code.data,
        'country': form.country.data,
    }
    schedule = {
        "schedule": form.schedule.data,
    }
    listing_data = {
        "highlights": form.highlights.data,
        "schedule": json.dumps(schedule),
        "cancellation_policy": form.cancellation_policy.data,
        "deposit_required": form.deposit_required.data,
        "age_requirement": form.age_requirement.data,
        "status": form.status.data,
    }

    if not business:
        flash("Failed to create tour listing. Please try again.", "danger")
        return render_template("auth/add_tour_listing.html", form=form)
    else:
        listings = {
            'title': form.title.data,
            'description': form.description.data,
            'address': json.dumps(address_data),
            'lattitude': form.lattitude.data,
            'longitude': form.longitude.data,
            'image_url': form.image_url.data,
            'business_type': 'hotel',
            'business_id': business['id'],
            'listing_data' : json.dumps(listing_data),
        }
        try:
            response = supabase.table('listings').insert(listings).execute()
        except Exception as e:
            print("Error creating listing:", e)
            return None
        return response.data[0]
    
def create_activity_listing():
    form = AddActivityListingForm()
    business = get_current_business()

    address_data = {
        'street': form.street.data,
        'city': form.city.data,
        'state': form.state.data,
        'postal_code': form.postal_code.data,
        'country': form.country.data,
    }

    listing_data = {
        "safety_measures": form.safety_measures.data,
        "waiver_required": form.waiver_required.data,
        "cancellation_policy": form.cancellation_policy.data,
        "age_requirement": form.age_requirement.data,
        "status": form.status.data,
        "equipment_provided": form.equipment_provided.data,
    }

    if not business:
        flash("Failed to create activity listing. Please try again.", "danger")
        return render_template("auth/add_activity_listing.html", form=form)
    else:
        listings = {
            'title': form.title.data,
            'description': form.description.data,
            'address': json.dumps(address_data),
            'lattitude': form.lattitude.data,
            'longitude': form.longitude.data,
            'image_url': form.image_url.data,
            'business_type': 'hotel',
            'business_id': business['id'],
            'listing_data' : json.dumps(listing_data),
        }
        try:
            response = supabase.table('listings').insert(listings).execute()
        except Exception as e:
            print("Error creating listing:", e)
            return None
        return response.data[0]



def update_listing(listing_id, data):
    """
    Update an existing listing in the database.
        Args:
            listing_id: The unique identifier of the listing to update
            data: Dictionary containing the fields to update
            
        Returns:
            The updated listing data if successful, None if an error occurs
            
    Raises:
        Prints error message if update fails
    """
    try:
        response = supabase.table('listings').update(data).eq('id', listing_id).execute()
    except Exception as e:
        print("Error updating listing:", e)
        return None
    return response.data[0]

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
