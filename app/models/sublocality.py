from app import db


class Sublocality(db.Model):
    __tablename__ = 'sublocalities'
    id = db.Column(db.Integer, primary_key=True)
    sublocality_code = db.Column(db.String(64), index=True)
    name = db.Column(db.String(64))
    locality_id = db.Column(db.String(64), db.ForeignKey('localities.id'))
    plots = db.relationship('Plot', backref='sublocality')
