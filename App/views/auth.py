from flask import Blueprint, render_template, request, flash, session, redirect, url_for, current_app
from App.supabase_client import supabase
from supabase_auth.errors import AuthApiError
from ..forms.auth import LoginForm, RegistrationForm, BusinessRegistrationForm, ResetPasswordRequestForm, ResetPasswordForm
from ..controllers.decorators import login_required
from ..controllers.base import fetch_business_types
from supabase_auth import VerifyTokenHashParams
from pydantic import ValidationError

auth_views = Blueprint('auth', __name__, template_folder='../templates')

@auth_views.route('/login', methods=['GET','POST'])
def login():
    """User login view."""
    form = LoginForm()
    next_url = request.args.get("next")
    print(f"Next URL: {next_url}")
    if form.validate_on_submit():

        try:
            # Supabase login attempt
            response = supabase.auth.sign_in_with_password(
                {"email": form.email.data, "password": form.password.data}
            )

        except AuthApiError:
            # Handles "Invalid login credentials" error cleanly
            flash("Invalid email or password.", "danger")
            return render_template("auth/login.html", form=form)

        except Exception as e:
            # Any unexpected error
            flash("Login error: " + str(e), "danger")
            return render_template("auth/login.html", form=form)

        # Save session tokens
        user = response.user
        role  = user.user_metadata.get("user_type") if user else None
        session_data = response.session
        if user and session_data:
            session["access_token"] = session_data.access_token
            session["refresh_token"] = session_data.refresh_token
            session["user_id"] = user.id if user else None
            session["user_role"] = role

            if role == "business":
                flash("Login successful!", "success")
                return redirect(url_for(next_url or "business.index"))
            else:
                flash("Login successful!", "success")
                return redirect(url_for(next_url or "main.index"))

    return render_template("auth/login.html", form=form, next=next_url)

@auth_views.route('/login/google')
def google_login():
    # Redirect user to Google's login page via Supabase
    # redirectTo must match your 'Site URL' or 'Redirect URLs' in Supabase settings
    res = supabase.auth.sign_in_with_oauth({
        "provider": "google",
        "options": {
            "redirect_to": "http://127.0.0.1:8080/auth/callback"
        }
    })
    return redirect(res.url)

@auth_views.route('/auth/callback')
def auth_callback():
    # Supabase handles the session via cookies/tokens automatically 
    # if using the Supabase Auth Helpers or JS client.
    # For a pure Flask backend, you may need to exchange the 'code' for a session.
    code = request.args.get('code')
    if code:
        response = supabase.auth.exchange_code_for_session({"auth_code": code})
        if response.session:
            session["access_token"] = response.session.access_token
            session["refresh_token"] = response.session.refresh_token
            session["user_id"] = response.user.id if response.user else None
            session["user_role"] = response.user.user_metadata.get("user_type") if response.user else None
    return redirect(url_for("main.index"))

@auth_views.route("/logout")
@login_required
def logout():
    """User logout view."""
    try:
        supabase.auth.sign_out()
        session.clear()
        flash("You have been logged out.", "info")
    except Exception as e:
        current_app.logger.exception("Logout error")
        flash("Logout error: " + str(e), "danger")

    return redirect(url_for("main.index"))


@auth_views.route("/register", methods=["GET", "POST"])
def register():
    """User registration view."""
    form = RegistrationForm()

    if form.validate_on_submit():
        try:
            response = supabase.auth.sign_up(
                {
                    "email": form.email.data,
                    "password": form.password.data,
                    "options": {
                        "data": {
                            "user_type": "regular", 
                            "is_business": False,
                            "first_name": form.first_name.data,  # Add this
                            "last_name": form.last_name.data     # Add this
                        }
                    }
                }
            )
        except Exception as e:
            current_app.logger.exception("Registration error")
            flash("Registration error: " + str(e), "danger")
            return render_template("auth/register.html", form=form)

        user = response.user
        if user:
            try:
                user_profile = {
                    "id": user.id,
                    "first_name": form.first_name.data,
                    "last_name": form.last_name.data,
                    "interests_handled": False
                }
                supabase.table("profiles").insert(user_profile).execute()
            except Exception:
                current_app.logger.exception("Failed to insert profile; continuing")

        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html", form=form)


@auth_views.route("/register-business", methods=["GET", "POST"])
def register_business():
    """Business user registration view."""
    # Fetch business types and initialize form
    type_choices = fetch_business_types()
    choices = [(str(bt["id"]), bt["name"]) for bt in type_choices]
    form = BusinessRegistrationForm(type_choices=choices)

    if form.validate_on_submit():
        is_profile_inserted = False
        try:
            signup_resp = supabase.auth.sign_up(
                {
                    "email": form.business_email.data,
                    "password": form.password.data,
                    "options": {"data": {"user_type": "business", "is_business": True}},
                }
            )
        except Exception as e:
            current_app.logger.exception("Supabase sign_up error")
            flash(f"Registration error: {e}", "danger")
            return render_template("auth/register_business.html", form=form)

        user = signup_resp.user
        session_data = signup_resp.session
        
        if user and session_data:
            # CRITICAL FIX: Set the session for RLS to pass the immediate insert
            session["access_token"] =session_data.access_token
            session["refresh_token"]=session_data.refresh_token
        
            
            try:
                selected_id = form.business_type.data
                # Re-validate business type ID just in case
                valid_ids = {c[0] for c in choices}
                if selected_id not in valid_ids:
                    raise ValueError("Invalid business type ID.")
                
                business_info = {
                    "user_id": user.id,
                    "business_name": form.business_name.data,
                    "business_email": form.business_email.data,
                    "business_type_id": selected_id,
                }
                supabase.table("businesses").insert(business_info).execute()
                
                is_profile_inserted = True # Set flag on successful DB insert

            except Exception:
                # This handles RLS failures, invalid IDs, or general DB issues
                current_app.logger.exception("Business profile creation error (RLS or DB)")
                flash("Business profile could not be created. Please contact support if the issue persists.", "warning")
            
            if is_profile_inserted:
                flash("Business registration successful! Welcome. Please log in.", "success")
                # Redirect user to login page after sign-out for email confirmation
                return redirect(url_for("auth.login"))
            else:
                # If sign_up succeeded but insert failed, re-render the form
                return render_template("auth/register_business.html", form=form)

        else:
            # Handles cases where sign_up was successful but user/session objects were unexpectedly missing
            flash("Registration failed or session data was incomplete. Please try again.", "danger")
            return render_template("auth/register_business.html", form=form)

    return render_template("auth/register_business.html", form=form)


@auth_views.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    """Password reset request view."""
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        email = form.email.data
        try:
            supabase.auth.reset_password_for_email(
                email
            )
            flash('If an account with that email exists, a password reset link has been sent to your email.', 'success')
        except Exception as e:
            current_app.logger.exception("Password reset request error")
            flash("Unable to send reset email: " + str(e), "danger")
        return redirect(url_for("auth.forgot_password"))
    
    return render_template("auth/forgot_password.html", form=form)


@auth_views.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    """Password reset view."""
    # If the request is POST, process the form submission
    form = ResetPasswordForm()
    if form.validate_on_submit():
        new_password = form.password.data
        try:
            supabase.auth.update_user({"password": new_password})

            supabase.auth.sign_out()
            flash(
                "Password reset successfully! Please log in with your new password.",
                "success",
            )
            return redirect(url_for("auth.login"))

        except Exception as e:
            # This catch handles API failure (e.g., session expired during form fill)
            print(f"Password reset error: {e}")
            flash(
                "Password update failed. Your session may have expired. Please try again.",
                "danger",
            )
            return render_template("auth/reset_password.html", form=form)

    return render_template("auth/reset_password.html", form=form)

@auth_views.route("/confirm")
def confirm():
    token_hash = request.args.get("token_hash")
    auth_type = request.args.get("type", "email")
    next = request.args.get("next", "main.index")

    if token_hash and auth_type:
        if auth_type == "recovery":
            session["password_update_required"] = True

        try:
            _ = supabase.auth.verify_otp(params=VerifyTokenHashParams(token_hash=token_hash, type=auth_type))
        except ValidationError as exception:
            flash("Validation error, please contact support", "danger")
    else:
        flash("Invalid confirmation link", "danger")
        return redirect(url_for("auth.login"))

    return redirect(url_for(next))