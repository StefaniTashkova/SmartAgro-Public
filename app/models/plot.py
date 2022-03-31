from app import db


class Plot(db.Model):
    __tablename__ = 'plots'
    id = db.Column(db.String(64), primary_key=True)
    area_by_doc = db.Column(db.Float(precision=5))
    area_workable = db.Column(db.Float(precision=5))
    category = db.Column(db.Integer)
    locality_id = db.Column(db.String(64), db.ForeignKey('localities.id'))
    sublocality_id = db.Column(db.String(64), db.ForeignKey('sublocalities.sublocality_code'))
    use_type_id = db.Column(db.Integer, db.ForeignKey('plot_use_types.id_use_type_code'))
    notes = db.Column(db.Text, nullable=True)
    ownerships = db.relationship('Ownership', backref='plot')
