import os
from flask import Flask, render_template
# from flask_uploads import DOCUMENTS, IMAGES, TEXT, UploadSet, configure_uploads
from flask_cors import CORS
from werkzeug.utils import secure_filename
from werkzeug.datastructures import  FileStorage
from flask_bootstrap import Bootstrap5

from App.database import init_db
from App.config import load_config


from App.controllers import (
    setup_jwt,
    add_auth_context
)

from App.views import views
from App.controllers.auth import get_business_profile, get_current_user, get_user_profile



def add_views(app):
    for view in views:
        app.register_blueprint(view)

def create_app(overrides={}):
    app = Flask(__name__, static_url_path='/static')
    load_config(app, overrides)
    CORS(app)
    add_auth_context(app)
    # photos = UploadSet('photos', TEXT + DOCUMENTS + IMAGES)
    # configure_uploads(app, photos)
    add_views(app)
    init_db(app)
    @app.context_processor
    def inject_current_user():
        user = get_current_user()  # call the function to get the actual user
        if user and user.user_metadata.get('is_business'):
            user_profile = get_business_profile(user)
        else:
            user_profile = get_user_profile(user) if user else None
        return {
            "current_user": user,
            "user_profile": user_profile
        }
    Bootstrap5(app)
    jwt = setup_jwt(app)
    # setup_admin(app)
    @jwt.invalid_token_loader
    @jwt.unauthorized_loader
    def custom_unauthorized_response(error):
        return render_template('401.html', error=error), 401
    app.app_context().push()
    
    
    return app