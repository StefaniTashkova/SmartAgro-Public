from enum import Enum

from app import db


class OwnerType(Enum):
    PERSON = 'физическо лице'
    COMPANY = 'юридическо лице'


class Owner(db.Model):
    __tablename__ = 'owners'
    id = db.Column(db.Integer, primary_key=True)
    owner_type = db.Column(db.String(128))
    name = db.Column(db.String(128))
    egn = db.Column(db.String(64))
    phone = db.Column(db.String(64))
    company_name = db.Column(db.String(128), nullable=True)
    company_number = db.Column(db.String(64), nullable=True)
    vat_number = db.Column(db.String(64), nullable=True)
    nationalID_number = db.Column(db.String(64), nullable=True)
    nationalID_issued_by = db.Column(db.String(128), nullable=True)
    nationalID_issue_date = db.Column(db.DateTime, nullable=True)
    IBAN = db.Column(db.String(128), nullable=True)
    BIC = db.Column(db.String(128), db.ForeignKey('banks.id_bic'), nullable=True)
    email = db.Column(db.String(64), unique=True, nullable=True)
    address = db.Column(db.String(128), nullable=True)
    payment_location = db.Column(db.String(128), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    ownerships = db.relationship('Ownership', backref='owner')
    contract_owners = db.relationship('ContractOwner', backref='owner')
