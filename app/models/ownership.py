from app import db


class Ownership(db.Model):
    __tablename__ = 'ownerships'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    plot_id = db.Column(db.String(64), db.ForeignKey('plots.id'))
    owner_id = db.Column(db.Integer, db.ForeignKey('owners.id'))
    total_owned_area = db.Column(db.Float(precision=3))
    owned_plot_fraction_numerator = db.Column(db.Integer)
    owned_plot_fraction_denominator = db.Column(db.Integer)
    additional_owned_area = db.Column(db.Float(precision=3))
    doc_number = db.Column(db.String(64), nullable=True)
    doc_date = db.Column(db.DateTime(), nullable=True)
    doc_path = db.Column(db.String(128), nullable=True)
    contract_subjects = db.relationship('ContractSubject', backref='ownership')
