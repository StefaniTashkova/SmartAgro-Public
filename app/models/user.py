from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import login_manager
from app import db


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    company_name = db.Column(db.String(128))
    company_number = db.Column(db.String(128))
    responsibleperson_name = db.Column(db.String(128))
    responsibleperson_id_number = db.Column(db.String(128))
    responsibleperson_egn = db.Column(db.String(128))
    IBAN = db.Column(db.String(128))
    BIC = db.Column(db.String(128), db.ForeignKey('banks.id_bic'))
    settings_file_path = (db.String(128))
    ownerships = db.relationship('Ownership', backref='user')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @classmethod
    def hash_password(cls, password):
        return generate_password_hash(password)

    @staticmethod
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    def __repr__(self):
        return '<User {}>'.format(self.username)
