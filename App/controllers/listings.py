from App.supabase_client import supabase
import random

def get_all_listings():
    """Get all listings from the database.
    
    Returns:
        list: List of all listings.
    """
    
    try:
        response=supabase.table('listings').select('*, business_types(name)').execute()
    except Exception as e:
        print("Error fetching listings:", e)
        return []
    print("Response data:", response.data)
    return response.data

def get_all_active_listings():
    """Get all active listings from the database.
    
    Returns:
        list: List of active listings.
    """
    try:
        response=supabase.table('listings').select('*, business_types(name)').eq('status', 'active').execute()
    except Exception as e:
        print("Error fetching active listings:", e)
        return []
    print("Response data:", response.data)
    return response.data

def get_listing_by_id(listing_id):
    """Get a listing by its ID.

    Args:
        listing_id (str): ID of the listing to retrieve (UUID or string).

    Returns:
        dict: The listing data if found, None otherwise.
    """
    try:
        response=supabase.table('listings').select('*, business_types(name)').eq('id',listing_id).single().execute()
    except Exception as e:
        print("Error fetching listing by id:", e)
        return None
    return response.data

def get_listing_details(listing_id):
    """Get detailed information for a listing by its ID."""
    try:
        listing_response = (
            supabase.table('listings')
            .select('business_types(name)')
            .eq('id', listing_id)
            .single()
            .execute()
        )

        listing_data = listing_response.data or {}

        # ✅ FIX: use dict access
        business_type_data = listing_data.get("business_types")

        if not business_type_data:
            return None

        business_type = (
            business_type_data.get("name", "")
            .strip()
            .lower()
        )

        table_by_type = {
            'hotel': 'hotel_details',
            'restaurant': 'restaurant_details',
            'activity': 'activity_details',
            'tour': 'tour_details',
            'tour operator': 'tour_operator_details',
        }

        details_table = table_by_type.get(business_type, 'listing_details')
        print(f"Fetching details from table: {details_table} for listing ID: {listing_id}")

        response = (
            supabase.table(details_table)
            .select('*')
            .eq('id', listing_id)
            .single()
            .execute()
        )
        print("Listing details response:", response.data)

        return response.data

    except Exception as e:
        print("Error fetching listing details:", e)
        return None


def search_listings(query):
    """Search listings based on provided query.

    Args:
        query (str): Query string to search listings.

    Returns:
        list: List of matching listings.
    """
    try:
        response=supabase.table('listings').select('*, business_types(name)').ilike('title',f'%{query}%').execute()
    except Exception as e:
        print("Error searching listings:", e)
        return []
    return response.data

def filter_listings(filters):
    """Filter listings based on provided criteria.

    Args:
        filters (dict): Dictionary containing filter criteria.

    Returns:
        list: List of filtered listings.
    """
    try:
        query = supabase.table('listings').select('*, business_types(name)')
        for key, value in filters.items():
            if value != "":
                if key == "query":
                    query = query.ilike('title', f'%{value}%')
                elif key == "category":
                    query = query.eq('business_type', value)
                elif key == "min_price":
                    query = query.gte('base_price', float(value))
                elif key == "max_price":
                    query = query.lte('base_price', float(value))
                elif key == "location":
                    query = query.ilike('address->>city', f'%{value}%')
        response = query.execute()
    except Exception as e:
        print("Error filtering listings:", e)
        return []
    return response.data

def sort_listings(listings, sort_by):
    """Sort listings based on specified criteria.

    Args:
        listings (list): List of listings to sort.
        sort_by (str): Sorting criteria ('price_low', 'price_high', 'rating', 'newest').

    Returns:
        list: Sorted list of listings.
    """
    if sort_by == "price-low":
        return sorted(listings, key=lambda x: x.get('base_price', 0))
    elif sort_by == "price-high":
        return sorted(listings, key=lambda x: x.get('base_price', 0), reverse=True)
    elif sort_by == "rating":
        return sorted(listings, key=lambda x: x.get('rating', 0), reverse=True)
    elif sort_by == "newest":
        return sorted(listings, key=lambda x: x.get('created_at', ''), reverse=True)
    return listings

def personalize_listings(user_interests):
    """Personalize listings based on user interests.

    Args:
        user_interests (list): List of user's interest IDs.

    Returns:
        list: Personalized list of listings, falling back to random active listings if none found.
    """
    if not user_interests:
        return get_all_active_listings()
    try:
        response = (
            supabase.table('listings')
            .select('*, business_types(name), listing_interests!inner(interest_id)')
            .in_('listing_interests.interest_id', user_interests)
            .eq('status', 'active')
            .limit(20)
            .execute()
        )
        listings = response.data or []
        print(f"Personalized listings found: {len(listings)} for interests: {user_interests}")

        if not listings:
            return get_all_active_listings()

        random.shuffle(listings)
        return listings
    except Exception as e:
        print("Error personalizing listings:", e)
        return get_all_active_listings()