import os
from datetime import date

from werkzeug.datastructures import FileStorage

from app.models import Payment, ContractOwner
from utils import ResourceManager, DocumentGenerator
from .abtract_channel import AbstractChannel
from .. import db


class PaymentChannel(AbstractChannel):

    @classmethod
    def generate_cash_payments(cls, user, owner_id, rent_per_unit_of_area, agricultural_year, cash_payment_date):
        contracts = [contract_owner.contract for contract_owner in
                     ContractOwner.query.filter(ContractOwner.owner_id == owner_id)]
        for contract in contracts:
            payment_exists = False
            for payment in contract.payments:
                if payment.agricultural_year == agricultural_year:
                    payment_exists = True
            if not payment_exists:
                payment = Payment(
                    date=date.today(),
                    agricultural_year=agricultural_year,
                    contract_id=contract.id,
                    status="НЕИЗПЪЛНЕНО",
                    type="РКО",
                )
                db.session.add(payment)
                db.session.commit()
                payment.doc_path = DocumentGenerator.generate_cash_payment(contract, payment, user,
                                                                           rent_per_unit_of_area, cash_payment_date)
                db.session.commit()

    @classmethod
    def generate_bank_payments(cls, user, owner_id, rent_per_unit_of_area, agricultural_year,
                               bank_payment_date, reason_for_bank_payment):
        contracts = [contract_owner.contract for contract_owner in
                     ContractOwner.query.filter(ContractOwner.owner_id == owner_id)]
        for contract in contracts:
            payment_exists = False
            for payment in contract.payments:
                if payment.agricultural_year == agricultural_year:
                    payment_exists = True
            if not payment_exists:
                payment = Payment(
                    date=date.today(),
                    agricultural_year=agricultural_year,
                    contract_id=contract.id,
                    status="НЕИЗПЪЛНЕНО",
                    type="Банков превод",
                )
                db.session.add(payment)
                db.session.commit()
                payment.doc_path = DocumentGenerator.generate_bank_payment(contract, user, rent_per_unit_of_area,
                                                                           bank_payment_date,
                                                                           reason_for_bank_payment)
                db.session.commit()

    @classmethod
    def edit_payment(cls, payment: Payment, doc_path, notes):
        old_path = payment.doc_path
        doc_path_changed = True if isinstance(doc_path, FileStorage) else False
        if doc_path_changed:
            local_path = ResourceManager.save_resource('payments', doc_path)
            payment.doc_path = local_path
        payment.notes = notes
        db.session.commit()
        if doc_path_changed:
            try:
                os.remove(old_path)
            except:
                pass

    @classmethod
    def delete_payment(cls, payment_id):
        payment = Payment.query.get(payment_id)
        if os.path.exists(payment.doc_path):
            os.remove(payment.doc_path)
        db.session.delete(payment)
        db.session.commit()
