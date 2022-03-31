from app import db


class ContractOwner(db.Model):
    __tablename__ = 'contract_owners'
    id = db.Column(db.Integer, primary_key=True)
    contract_id = db.Column(db.String(64), db.ForeignKey('contracts.id'))
    owner_id = db.Column(db.Integer, db.ForeignKey('owners.id'))
