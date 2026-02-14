from flask import Blueprint, render_template, flash, session, redirect, url_for
from flask_wtf import FlaskForm
from supabase import AuthApiError, FunctionsRelayError, FunctionsHttpError
from postgrest.exceptions import APIError
from App.supabase_client import supabase
from App.forms.account import ProfileForm, UpdateEmailForm, UpdatePasswordForm
from ..controllers.auth import get_current_user
from ..controllers.decorators import login_required, role_required
from ..controllers.account import user_to_profile_form_data

account_views = Blueprint('account_views', __name__, template_folder='../templates', url_prefix='/account')

@account_views.route("/")
@login_required
@role_required("regular")
def profile():
    """User profile view."""
    user = get_current_user()
    return render_template("account/index.html", user=user)

@account_views.route("/update", methods=["GET", "POST"])
@login_required
@role_required("regular")
def update():
    """Update user profile."""
    user = get_current_user()
    form = ProfileForm(data=user_to_profile_form_data(user))
    if form.validate_on_submit():
        first_name = form.first_name.data
        last_name = form.last_name.data
        phone_number = form.phone_number.data
        avatar = form.avatar.data
        birth_date = form.birth_date.data
        avatar_url = None
        if avatar:
            file_bytes = avatar.read()

            file_ext = avatar.filename.rsplit('.', 1)[-1]
            file_name = f"avatars/{user.id}.{file_ext}"

            supabase.storage.from_("avatars").upload(
                file_name,
                file_bytes,
                {"content-type": avatar.mimetype}
            )

            avatar_url = supabase.storage.from_("avatars").get_public_url(file_name)
            
        update_data = {
            "p_user_id": user.id,
            "p_first_name": first_name,
            "p_last_name": last_name,
            "p_phone_number": phone_number,
            "p_birth_date": birth_date.isoformat() if birth_date else None,
            "p_avatar_url": avatar_url if avatar_url else user.user_metadata.get("avatar_url"),
        }
        
        try:
            response = supabase.rpc(fn="update_profile", params=update_data,
            ).execute()
            if response:
                flash("Your profile was updated successfully.", "info")
            else:
                flash(
                    "Updating your profile failed, please try again.",
                    "danger",
                )
        except APIError as exception:
            flash(exception.message, "danger")

    return render_template("account/update.html", form=form, user=user)

@account_views.route("/update-email", methods=["GET", "POST"])
@login_required
@role_required("regular")
def update_email():
    user = get_current_user()
    form = UpdateEmailForm()
    if form.validate_on_submit():
        email = form.email.data

        try:
            user = supabase.auth.update_user(attributes={"email": email})

            if user:
                flash("Your email was updated successfully.", "info")
            else:
                flash(
                    "Updating your email address failed, please try again.",
                    "error",
                )
        except AuthApiError as exception:
            err = exception.to_dict()
            flash(err.get("message"), "error")

    return render_template("account/update-email.html", form=form, user=user)


@account_views.route("/update-password", methods=["GET", "POST"])
@login_required
@role_required("regular")
def update_password():
    user = get_current_user()
    form = UpdatePasswordForm()
    if form.validate_on_submit():
        password = form.password.data

        try:
            user = supabase.auth.update_user(attributes={"password": password})

            if user:
                flash("Your password was updated successfully.", "info")
                session.pop("password_update_required", None)
            else:
                flash("Updating your password failed, please try again.", "error")
        except AuthApiError as exception:
            err = exception.to_dict()
            flash(err.get("message"), "error")

    return render_template("account/update-password.html", form=form, profile=profile)
    
@account_views.route("/delete/confirm")
@login_required
@role_required("regular")
def destroy():
    user = get_current_user()
    return render_template("account/delete.html", user=user)

@account_views.route("/delete/confirm", methods=["POST"])
@login_required
def destroy_confirm():
    form = FlaskForm()
    if form.is_submitted():
        try:
            r = supabase.functions.invoke("delete-account")

            if r:
                flash("Your account has been successfully deleted.", "info")
                supabase.auth.sign_out()
                return redirect(url_for("main.index"))
            else:
                flash(
                    "We couldn't delete your account, please contact support.", "error"
                )
                return redirect(url_for("account.home"))
        except (FunctionsRelayError, FunctionsHttpError) as exception:
            err = exception.to_dict()
            flash(err.get("message"), "error")
            return redirect(url_for("account.profile"))    