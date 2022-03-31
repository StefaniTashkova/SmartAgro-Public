import os

from werkzeug.datastructures import FileStorage

from app import db
from app.models import Contract, ContractOwner, ContractSubject, Ownership
from utils import DocumentGenerator, ResourceManager
from .payment_channel import PaymentChannel
from .abtract_channel import AbstractChannel


class ContractChannel(AbstractChannel):

    @classmethod
    def add_contract(cls, owner_id, plot_ids, contract_type, date_signed, date_started, duration_years, notes,
                     date_signed_for_generated_contracts, date_started_for_generated_contracts,
                     kg_per_dka_for_generated_contracts, *args, **kwargs):
        ownerships = Ownership.query.filter_by(owner_id=owner_id).all()
        selected_ownerships = [ownership for ownership in ownerships if ownership.plot_id in plot_ids]
        if not selected_ownerships:
            raise ValueError("Zero plots selected")
        ownerships_by_locality = {locality_id: [] for locality_id in
                                  set([ownership.plot.locality_id for ownership in selected_ownerships])}
        for ownership in selected_ownerships:
            ownerships_by_locality[ownership.plot.locality_id].append(ownership)
        # Create a contract for each locality
        for locality_id, ownerships in ownerships_by_locality.items():
            first_agricultural_year = date_started.date().year if date_started.date().month < 10 else date_started.date().year + 1
            i = 1
            contract_id = f"{locality_id}_{owner_id}_{first_agricultural_year}_{i}"
            while Contract.query.get(contract_id):
                i += 1
                contract_id = f"{locality_id}_{owner_id}_{first_agricultural_year}_{i}"
            doc_path = DocumentGenerator.generate_contract(ownerships, date_signed_for_generated_contracts,
                                                           date_started_for_generated_contracts,
                                                           kg_per_dka_for_generated_contracts,
                                                           duration_years, contract_id)
            contract = Contract(id=contract_id, date_signed=date_signed, date_started=date_started,
                                first_agricultural_year=first_agricultural_year, contract_type=contract_type,
                                duration_years=duration_years, locality_id=locality_id, doc_path=doc_path,
                                notes=notes)
            contract_owner = ContractOwner(contract_id=contract_id, owner_id=owner_id)
            contract_subjects = [
                ContractSubject(contract_id=contract_id, ownership_id=ownership.id) for ownership in ownerships]
            db.session.add(contract)
            db.session.add(contract_owner)
            for subject in contract_subjects:
                db.session.add(subject)
        db.session.commit()


    @classmethod
    def edit_contract(cls, contract: Contract, doc_path, notes):
        old_path = contract.doc_path
        doc_path_changed = True if isinstance(doc_path, FileStorage) else False
        if doc_path_changed:
            local_path = ResourceManager.save_resource('contracts', doc_path)
            contract.doc_path = local_path
        contract.notes = notes
        db.session.commit()
        if doc_path_changed:
            try:
                os.remove(old_path)
            except:
                pass

    @classmethod
    def delete_contract(cls, contract_id):
        contract = Contract.query.get(contract_id)
        for payment in contract.payments:
            PaymentChannel.delete_payment(payment.id)
        for contract_owner in contract.contract_owners:
            db.session.delete(contract_owner)
        for contract_subject in contract.contract_subjects:
            db.session.delete(contract_subject)
        if os.path.exists(contract.doc_path):
            os.remove(contract.doc_path)
        db.session.delete(contract)
        db.session.commit()
