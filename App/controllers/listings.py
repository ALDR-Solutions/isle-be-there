from App.supabase_client import supabase

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
def get_active_listing_by_id(listing_id):
    """Get a listing by its ID.

    Args:
        listing_id (str): ID of the listing to retrieve (UUID or string).

    Returns:
        dict: The listing data if found, None otherwise.
    """
    try:
        response=supabase.table('listings').select('*, business_types(name)').eq('status', "active").eq('id',listing_id).single().execute()
    except Exception as e:
        print("Error fetching listing by id:", e)
        return None
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

def get_active_listings():
    """Get all active listings from the database.

    Returns:
        list: List of active listings.
    """
    try:
        response = supabase.table('listings').select('*, business_types(name)').eq('status', "active").execute()
    except Exception as e:
        print("Error fetching active listings:", e)
        return []
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
            .eq('listing_id', listing_id)
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

def filter_active_listings(filters):
    """Filter active listings based on provided criteria.

    Args:
        filters (dict): Dictionary containing filter criteria.

    Returns:
        list: List of filtered listings.
    """
    try:
        query = supabase.table('listings').select('*, business_types(name)').eq('status', "active")
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
    def price_key(x, descending=False):
        price = x.get("base_price")

        # Always push NULL prices to the end
        if price is None:
            return (1, 0)

        return (0, -price if descending else price)

    if sort_by == "price-low":
        return sorted(listings, key=lambda x: price_key(x))

    elif sort_by == "price-high":
        return sorted(listings, key=lambda x: price_key(x, descending=True))

    elif sort_by == "rating":
        return sorted(
            listings,
            key=lambda x: x.get("rating") or 0,
            reverse=True
        )

    elif sort_by == "newest":
        return sorted(
            listings,
            key=lambda x: x.get("created_at") or "",
            reverse=True
        )

    return listings