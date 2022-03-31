from app import db


class Locality(db.Model):
    __tablename__ = 'localities'
    id = db.Column(db.String(64), primary_key=True)
    region = db.Column(db.String(64))
    municipality = db.Column(db.String(64))
    name = db.Column(db.String(64))
    plots = db.relationship('Plot', backref='locality')
    sublocalities = db.relationship('Sublocality', backref='locality')
    contracts = db.relationship('Contract', backref='locality')
