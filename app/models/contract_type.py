from app import db


class ContractType(db.Model):
    __tablename__ = 'contract_types'
    id_contract_type = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    contracts = db.relationship('Contract', backref='contract_type_ref')
