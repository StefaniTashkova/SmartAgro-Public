from flask import request, g, session
from flask_login import current_user
from . import app

LOGIN_REQUIRED_PATHS = ['/user', '/owners', '/plots', '/contracts', '/payments', '/static/user_data']


def authenticate():
    if any([True for path in LOGIN_REQUIRED_PATHS if request.path.startswith(path)]):
        # Request is trying to access a protected path
        if not current_user.is_authenticated:
            return app.login_manager.unauthorized()
    return None
