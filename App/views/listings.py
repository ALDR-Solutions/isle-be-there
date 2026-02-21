from flask import render_template, request, redirect, url_for, Blueprint, flash
from App.supabase_client import supabase
from ..controllers.listings import get_all_listings, get_listing_by_id, filter_listings, sort_listings, get_listing_details

listings_view = Blueprint('listings', __name__, template_folder='../templates', url_prefix='/listings')

@listings_view.route('/', methods=['GET'])
def list_listings():
    business_types = (supabase.table('business_types').select('*').execute()).data or []
    filters = request.args.to_dict()
    print("Filters received:", filters)
    listings = filter_listings(filters) if filters else get_all_listings()
    sort_by = request.args.get('sort')
    if sort_by:
        listings = sort_listings(listings, sort_by)
    return render_template('listings/list.html', listings=listings, business_types=business_types)

@listings_view.route('/<listing_id>', methods=['GET'])
def view_listing(listing_id):
    listing = get_listing_by_id(listing_id)
    if not listing:
        flash('Listing not found.', 'warning')
        return redirect(url_for('listings.list_listings'))
    listing_details = get_listing_details(listing_id)
    return render_template('listings/list_details.html', listing=listing, listing_details=listing_details)




