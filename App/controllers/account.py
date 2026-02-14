def user_to_profile_form_data(user):
    """Extracts profile fields from Supabase user into a dict for WTForms prefill."""
    meta = user.user_metadata or {}

    return {
        "first_name": meta.get("first_name", ""),
        "last_name": meta.get("last_name", ""),
        "phone_number": meta.get("phone_number", ""),
        "birth_date": meta.get("birth_date", None),
        # avatar is NOT prefilled (file inputs cannot have default values)
    }