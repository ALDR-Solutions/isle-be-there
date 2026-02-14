from functools import wraps
from flask import redirect, request, url_for, flash, session
from .auth import get_current_user

def login_required(f):
    """Supabase-based login_required decorator."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not get_current_user():
            flash("Please log in first.", "warning")
            return redirect(url_for("auth.login", next=request.endpoint))
        return f(*args, **kwargs)

    return decorated

def role_required(role):
    """Supabase-based role_required decorator."""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            user = get_current_user()
            
            # Check if user exists and role matches
            if not user or user.user_metadata.get("user_type") != role:
                flash("You do not have permission to access this page.", "warning")
                return redirect(url_for("auth.login"))

            return f(*args, **kwargs)

        return decorated

    return decorator 

def password_update_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "password_update_required" in session:
            flash(
                """
                Almost there! Update your password first, and you’ll unlock the 
                rest of the site right away.
                """, 
                "info"
            )
            return redirect(url_for("account.update_password"))

        return f(*args, **kwargs)

    return decorated
