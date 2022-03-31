from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_scss import Scss
from flask_sqlalchemy import SQLAlchemy

from .config import Config

app = Flask(__name__, template_folder='views')
app.config.from_object(Config)
login_manager = LoginManager(app)
mail = Mail(app)
db = SQLAlchemy(app)

from . import models

migrate = Migrate(app, db)

app.before_request(Scss(app, static_dir='app/static/css', asset_dir='app/assets/scss').update_scss)

from .middlewares import authenticate

app.before_request(authenticate)

from . import routes  # This line can cause the flask-migrate to fail, comment it when setting up the DB
