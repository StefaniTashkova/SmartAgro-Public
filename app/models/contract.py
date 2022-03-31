from app import db


class Contract(db.Model):
    __tablename__ = 'contracts'
    id = db.Column(db.String(64), primary_key=True)
    date_signed = db.Column(db.DateTime)
    date_started = db.Column(db.DateTime)
    first_agricultural_year = db.Column(db.Integer)
    contract_type = db.Column(db.Integer, db.ForeignKey('contract_types.id_contract_type'))
    duration_years = db.Column(db.Integer)
    locality_id = db.Column(db.String(64), db.ForeignKey('localities.id'))
    doc_path = db.Column(db.String(128))
    notes = db.Column(db.Text, nullable=True)
    contract_owners = db.relationship('ContractOwner', backref='contract')
    contract_subjects = db.relationship('ContractSubject', backref='contract')
    contract_type_id = db.relationship('ContractType', backref='contract')
    payments = db.relationship('Payment', backref='contract')
