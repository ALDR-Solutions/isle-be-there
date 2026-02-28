from flask_jwt_extended import create_access_token, jwt_required, JWTManager, get_jwt_identity, verify_jwt_in_request
from App.supabase_client import supabase
from flask import current_app, session


    
def get_current_user():
    """Return authenticated Supabase user from session JWT with profile data."""
    access_token = get_valid_access_token()
    if not access_token:
        print("No access token found in session")
        return None

    try:
        user_resp = supabase.auth.get_user(access_token)
        user = user_resp.user
        
        if not user:
            return None
        
        return user
        
    except Exception as e:
        current_app.logger.error(f"Error getting current user: {e}")
        return None

def get_user_profile(user):
    profile_info = {}

    if not user:
        return profile_info

    try:
        profile_response = (
            supabase.table("profiles")
            .select("*")
            .eq("user_id", user.id)
            .maybe_single()
            .execute()
        )

        db_profile = getattr(profile_response, "data", None)  # None if no row found
        
        if not db_profile:
            current_app.logger.info(f"No profile found for user {user.id}")
            return profile_info

        first = db_profile.get("first_name", "") or ""
        last = db_profile.get("last_name", "") or ""

        profile_info = {
            "first_name": first,
            "last_name": last,
            "full_name": f"{first} {last}".strip(),
            "avatar_url": db_profile.get("avatar_url"),
            "phone_number": db_profile.get("phone"),
            "birth_date": db_profile.get("birth_date"),
            "interests_handled": db_profile.get("interests_handled", False),
            "id": db_profile.get("id"),
        }

    except Exception as err:
        current_app.logger.warning(f"Could not fetch profile for user {user.id}: {err}")

    return profile_info

def get_business_profile(user):
    profile_info = {}

    if not user:
        return profile_info

    try:
        profile_response = (
            supabase.table("businesses")
            .select("*")
            .eq("user_id", user.id)
            .maybe_single()
            .execute()
        )

        if not profile_response:
            current_app.logger.warning(f"No response from Supabase for business {user.id}")
            return profile_info

        db_profile = getattr(profile_response, "data", None)
        if not db_profile:
            current_app.logger.info(f"No profile data found for business {user.id}")
            return profile_info

        name = db_profile.get("business_name", "") or ""

        profile_info = {
            "business_name": name,
            "logo_url": db_profile.get("logo_url"),
            "phone": db_profile.get("phone"),
            "id": db_profile.get("id"),
        }

    except Exception as err:
        current_app.logger.warning(f"Could not fetch profile for business {user.id}: {err}")

    return profile_info

def get_valid_access_token():
    """Return a valid access token, refreshing it if expired."""
    access_token = session.get("access_token")
    refresh_token = session.get("refresh_token")

    if not access_token or not refresh_token:
        return None  # User not logged in

    try:
        # Try to get the user with current access token
        user_resp = supabase.auth.get_user(access_token)
        if user_resp.user:
            return access_token
        else:
            # Access token expired, attempt refresh
            refresh_resp = supabase.auth.refresh_session(refresh_token)
            if not refresh_resp.session:
                current_app.logger.warning("Could not refresh access token.")
                return None

            # Update session with new tokens
            session["access_token"] = refresh_resp.session.access_token
            session["refresh_token"] = refresh_resp.session.refresh_token
            return refresh_resp.session.access_token

    except Exception as e:
        current_app.logger.error(f"Error validating/refreshing token: {e}")
        session.clear()
        return None