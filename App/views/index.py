from flask import Blueprint, render_template, request, jsonify, current_app, flash
from App.supabase_client import supabase
from App.controllers.auth import get_current_user, get_user_profile
from App.controllers.base import get_all_interests


index_views = Blueprint('main', __name__, template_folder='../templates')

@index_views.route('/')
def index():
    user = get_current_user()
    show_interests = False
    interests = []
    if user:
        profile = get_user_profile(user)
        # Show popup only if interests_handled is False
        show_interests = not profile.get('interests_handled', True)
        print("User profile interests_handled:", profile.get('interests_handled'))
        if show_interests:
            interests = get_all_interests()
    return render_template('index.html', show_interests=show_interests, interests=interests)


@index_views.route('/save-interests', methods=['POST'])
def save_interests():
    user = get_current_user()
    if not user:
        flash("Please log in to save your interests.", "warning")
        return jsonify({'error': 'Unauthorized'}), 401
        

    data = request.get_json()
    interest_ids = data.get('interests', [])
    if not isinstance(interest_ids, list):
        flash("Invalid data format for interests.", "danger")
        return jsonify({'error': 'Invalid data'}), 400

    try:
        # Remove any existing entries for this user
        supabase.table("user_interests").delete().eq("user_id", user.id).execute()

        # Insert new selections
        for interest_id in interest_ids:
            supabase.table("user_interests").insert({
                "user_id": user.id,
                "interest_id": interest_id
            }).execute()

        # Mark as handled
        supabase.table("profiles").update({"interests_handled": True}).eq("id", user.id).execute()

        return jsonify({'success': True})
    except Exception as e:
        flash("An error occurred while saving your interests. Please try again.", "danger")
        current_app.logger.error(f"Error saving interests: {e}")
        return jsonify({'error': str(e)}), 500

@index_views.route('/skip-interests', methods=['POST'])
def skip_interests():
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        # Just mark as handled, no interests inserted
        supabase.table("profiles").update({"interests_handled": True}).eq("id", user.id).execute()
        return jsonify({'success': True})
    except Exception as e:
        flash("An error occurred while skipping your interests. Please try again.", "danger")
        current_app.logger.error(f"Error skipping interests: {e}")
        return jsonify({'error': str(e)}), 500