from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, session
from ..controllers.decorators import login_required



bookings_view = Blueprint('bookings', __name__, template_folder='../templates', url_prefix='/bookings')


