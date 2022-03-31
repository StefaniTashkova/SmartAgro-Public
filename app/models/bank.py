from app import db


class Bank(db.Model):
    __tablename__ = 'banks'
    id_bic = db.Column(db.String(64), primary_key=True)
    name = db.Column(db.String(64))
    users = db.relationship('User', backref='bank')
    owners = db.relationship('Owner', backref='bank')
