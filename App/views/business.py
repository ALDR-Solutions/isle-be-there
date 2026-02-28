from flask import redirect, render_template, request, url_for, Blueprint, flash
from ..controllers.decorators import role_required

business_view = Blueprint('business', __name__, template_folder='../templates/business', url_prefix='/business')

