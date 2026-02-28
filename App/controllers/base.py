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
    countries = [
        "Antigua and Barbuda",
        "Bahamas",
        "Barbados",
        "Belize",
        "Cuba",
        "Dominica",
        "Dominican Republic",
        "Grenada",
        "Guyana",
        "Haiti",
        "Jamaica",
        "Saint Kitts and Nevis",
        "Saint Lucia",
        "Saint Vincent and the Grenadines",
        "Suriname",
        "Trinidad and Tobago",
    ]
    return countries    