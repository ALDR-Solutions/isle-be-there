from flask import current_app
from App.supabase_client import supabase

def fetch_business_types():
    """Return list of dicts [{'id':..., 'name':...}, ...] or [] on error."""
    try:
        resp = supabase.table("business_types").select("id,name").execute()
        data = getattr(resp, "data", None) or (resp.get("data") if isinstance(resp, dict) else None)
        print(data)
        return data or []
    except Exception:
        current_app.logger.exception("Failed to fetch business types")
        return []
    
def get_caribbean_countries():
    """Return list of Caribbean countries."""
    return [
        "Antigua and Barbuda", "Bahamas", "Barbados", "Belize", "Dominica",
        "Grenada", "Guyana", "Haiti", "Jamaica", "Saint Kitts and Nevis",
        "Saint Lucia", "Saint Vincent and the Grenadines", "Suriname",
        "Trinidad and Tobago"
    ]
    
def get_all_interests():
    """Return list of dicts [{'id':..., 'name':...}, ...] or [] on error."""
    try:
        resp = supabase.table("interests").select("id,name,category").execute()
        print(f"This is your data {resp.data}")
        data = getattr(resp, "data", None) or (resp.get("data") if isinstance(resp, dict) else None)
        print(data)
        return data or []
    except Exception:
        current_app.logger.exception("Failed to fetch interests")
        return []

def get_user_interests(user_id):
    """Return list of interest IDs for a given user."""
    try:
        resp = supabase.table("user_interests").select("interest_id").eq("user_id", user_id).execute()
        data = getattr(resp, "data", None) or (resp.get("data") if isinstance(resp, dict) else None)
        return [item["interest_id"] for item in (data or [])]
    except Exception:
        current_app.logger.exception(f"Failed to fetch interests for user {user_id}")
        return []
