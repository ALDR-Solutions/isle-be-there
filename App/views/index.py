from flask import Blueprint, render_template

index_views = Blueprint('main', __name__, template_folder='../templates')

@index_views.route('/')
def index():
    return render_template('index.html')