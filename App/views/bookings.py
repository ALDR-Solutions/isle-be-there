from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, session
from ..controllers.decorators import login_required
from ..controllers.bookings import (
    create_hotel_booking,
    confirm_hotel_booking,
    cancel_hotel_booking,
    get_booking_by_id,
)


bookings_view = Blueprint('bookings', __name__, template_folder='../templates', url_prefix='/bookings')


@bookings_view.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    if request.method == 'GET':
        return render_template('bookings/checkout.html')

    listing_id = request.form.get('listing_id') or request.args.get('listing_id')
    room_type_id = request.form.get('room_type_id') or request.args.get('room_type_id')
    check_in = request.form.get('check_in')
    check_out = request.form.get('check_out')

    adults = request.form.get('adults', 1)
    children = request.form.get('children', 0)
    quantity = request.form.get('quantity', 1)
    currency = request.form.get('currency', 'USD')

    if not listing_id or not room_type_id or not check_in or not check_out:
        flash('Missing booking details. Please select dates and room type.', 'warning')
        return redirect(url_for('listings.list_listings'))

    user_id = session.get('user_id')

    payload = {
        'p_listing_id': listing_id,
        'p_user_id': user_id,
        'p_check_in': check_in,
        'p_check_out': check_out,
        'p_adults': int(adults),
        'p_children': int(children),
        'p_room_type_id': room_type_id,
        'p_quantity': int(quantity),
        'p_currency': currency,
    }

    booking_id = create_hotel_booking(payload)

    if not booking_id:
        flash('Booking failed. Please try different dates or room quantity.', 'danger')
        return redirect(url_for('listings.list_listings'))

    flash('Booking created successfully. Complete payment to confirm.', 'success')
    return redirect(url_for('bookings.view_booking', booking_id=booking_id))


@bookings_view.route('/<booking_id>', methods=['GET'])
@login_required
def view_booking(booking_id):
    booking = get_booking_by_id(booking_id)
    if not booking:
        flash('Booking not found.', 'warning')
        return redirect(url_for('listings.list_listings'))

    return jsonify({'booking': booking})


@bookings_view.route('/create', methods=['POST'])
@login_required
def create_booking_api():
    data = request.get_json(silent=True) or {}
    data['p_user_id'] = session.get('user_id')

    booking_id = create_hotel_booking(data)
    if not booking_id:
        return jsonify({'ok': False, 'message': 'Unable to create booking'}), 400

    return jsonify({'ok': True, 'booking_id': booking_id}), 201


@bookings_view.route('/<booking_id>/confirm', methods=['POST'])
@login_required
def confirm_booking(booking_id):
    confirmed = confirm_hotel_booking(booking_id)
    if not confirmed:
        return jsonify({'ok': False, 'message': 'Booking confirmation failed'}), 400

    return jsonify({'ok': True, 'booking_id': booking_id})


@bookings_view.route('/<booking_id>/cancel', methods=['POST'])
@login_required
def cancel_booking(booking_id):
    cancelled = cancel_hotel_booking(booking_id)
    if not cancelled:
        return jsonify({'ok': False, 'message': 'Booking cancellation failed'}), 400

    return jsonify({'ok': True, 'booking_id': booking_id})
