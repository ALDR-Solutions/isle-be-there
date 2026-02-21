from flask_jwt_extended import create_access_token, jwt_required, JWTManager, get_jwt_identity, verify_jwt_in_request
from App.supabase_client import supabase
from flask import current_app, session
from App.models import User
from App.database import db

def login(username, password):
  result = db.session.execute(db.select(User).filter_by(username=username))
  user = result.scalar_one_or_none()
  if user and user.check_password(password):
    # Store ONLY the user id as a string in JWT 'sub'
    return create_access_token(identity=str(user.id))
  return None


def setup_jwt(app):
  jwt = JWTManager(app)

  # Always store a string user id in the JWT identity (sub),
  # whether a User object or a raw id is passed.
  @jwt.user_identity_loader
  def user_identity_lookup(identity):
    user_id = getattr(identity, "id", identity)
    return str(user_id) if user_id is not None else None

  @jwt.user_lookup_loader
  def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    # Cast back to int primary key
    try:
      user_id = int(identity)
    except (TypeError, ValueError):
      return None
    return db.session.get(User, user_id)

  return jwt


# Context processor to make 'is_authenticated' available to all templates
def add_auth_context(app):
  @app.context_processor
  def inject_user():
      try:
          verify_jwt_in_request()
          identity = get_jwt_identity()
          user_id = int(identity) if identity is not None else None
          current_user = db.session.get(User, user_id) if user_id is not None else None
          is_authenticated = current_user is not None
      except Exception as e:
          print(e)
          is_authenticated = False
          current_user = None
      return dict(is_authenticated=is_authenticated, current_user=current_user)
    
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

def get_user_profile(user: User) -> dict:
    profile_info = {}

    if not user:
        return profile_info

    try:
        profile_response = (
            supabase.table("profiles")
            .select("*")
            .eq("id", user.id)
            .maybe_single()
            .execute()
        )

        if not profile_response:
            current_app.logger.warning(f"No response from Supabase for user {user.id}")
            return profile_info

        db_profile = getattr(profile_response, "data", None)
        if not db_profile:
            current_app.logger.info(f"No profile data found for user {user.id}")
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
            "id": db_profile.get("id"),
        }

    except Exception as err:
        current_app.logger.warning(f"Could not fetch profile for user {user.id}: {err}")

    return profile_info

def get_business_profile(user: User) -> dict:
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