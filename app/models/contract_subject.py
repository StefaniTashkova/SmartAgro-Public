from app import db


class ContractSubject(db.Model):
    __tablename__ = 'contract_subjects'
    id = db.Column(db.Integer, primary_key=True)
    contract_id = db.Column(db.String(64), db.ForeignKey('contracts.id'))
    ownership_id = db.Column(db.Integer, db.ForeignKey('ownerships.id'))
