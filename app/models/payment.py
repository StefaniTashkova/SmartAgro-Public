from app import db


class Payment(db.Model):
    __tablename__ = 'payments'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime)
    agricultural_year = db.Column(db.String(64))
    contract_id = db.Column(db.String(64), db.ForeignKey('contracts.id'))
    paid_amount_bgn = db.Column(db.Float(precision=2))
    grain_weight = db.Column(db.Float(precision=2))
    grain_type = db.Column(db.String(64))
    mixed_grain_weight = db.Column(db.Float(precision=2))
    mixed_grain_holder = db.Column(db.String(64))
    status = db.Column(db.String(45))
    notes = db.Column(db.Text, nullable=True)
    doc_path = db.Column(db.String(128))
    type = db.Column(db.String(128))
