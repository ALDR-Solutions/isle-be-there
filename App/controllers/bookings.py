from App.supabase_client import supabase


def create_hotel_booking(payload):
    """Create a hotel booking through RPC and return booking id."""
    response = supabase.rpc('create_hotel_booking', payload).execute()
    data = response.data

    if isinstance(data, list):
        return data[0] if data else None
    return data


def confirm_hotel_booking(booking_id):
    """Confirm an existing pending hotel booking."""
    response = supabase.rpc('confirm_hotel_booking', {'p_booking_id': booking_id}).execute()
    return bool(response.data)


def cancel_hotel_booking(booking_id):
    """Cancel a booking and release future inventory."""
    response = supabase.rpc('cancel_hotel_booking', {'p_booking_id': booking_id}).execute()
    return bool(response.data)


def get_booking_by_id(booking_id):
    """Fetch a booking by id."""
    response = (
        supabase.table('hotel_bookings')
        .select('*, hotel_booking_items(*)')
        .eq('id', booking_id)
        .single()
        .execute()
    )
    return response.data
