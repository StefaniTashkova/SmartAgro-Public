import json
import os
import time
import traceback
from copy import copy
from datetime import date
from io import BytesIO
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED

from flask import render_template, request, redirect, flash, send_file
from flask.helpers import url_for
from flask_login import current_user
from werkzeug.datastructures import FileStorage

from app import app, db
from app.forms import AddContractForm, EditContractForm
from app.models import Contract, Ownership, Owner, Locality, User
from utils import ResourceManager
from .paginated_search_controller import PaginatedSearchController
from ..channels import ContractChannel


class ContractController:

    @classmethod
    def render_contracts_page(cls):
        form = AddContractForm()
        contracts, next_url, prev_url, query = PaginatedSearchController.paginate(Contract, 'contracts')
        owners = Owner.query.all()
        localities = Locality.query.all()
        ownerships = Ownership.query.all()
        owner_id = request.args.get('owner_id')
        for ownership in ownerships:
            first_available_year = date.today().year if date.today().month < 10 else date.today().year + 1
            ownership_contracts = [subject.contract for subject in ownership.contract_subjects]
            for contract in ownership_contracts:
                contract_first_agricultural_year = contract.date_started.date().year \
                    if contract.date_started.date().month < 10 \
                    else contract.date_started.date().year + 1
                first_year_after_contract = contract_first_agricultural_year + contract.duration_years
                if first_year_after_contract > first_available_year:
                    first_available_year = first_year_after_contract
            ownership.first_available_year = first_available_year
        return render_template('contracts/contracts.html', contracts=contracts, next_url=next_url, prev_url=prev_url,
                               form=form, owners=owners, localities=localities, ownerships=ownerships,
                               query=query, owner_id=owner_id)

    @classmethod
    def render_contract_page(cls, contract_id):
        contract = Contract.query.get(contract_id)
        owners = [contract_owner.owner for contract_owner in contract.contract_owners]
        ownerships = [contract_subjects.ownership for contract_subjects in contract.contract_subjects]
        form = EditContractForm(obj=contract)
        if contract.doc_path:
            try:
                stored_doc_path = url_for('static', filename=contract.doc_path.split('static\\')[1].replace('\\', '/'))
            except:
                stored_doc_path = None
        else:
            stored_doc_path = None
        return render_template('contracts/contract.html', contract=contract, form=form, stored_doc_path=stored_doc_path,
                               owners=owners, ownerships=ownerships)

    @classmethod
    def add_contract(cls):
        form = AddContractForm()
        contracts, next_url, prev_url, query = PaginatedSearchController.paginate(Contract, 'contracts')
        owners = Owner.query.all()
        localities = Locality.query.all()
        ownerships = Ownership.query.all()
        owner_id = request.args.get('owner_id', None, type=int)
        user = User.query.get_or_404(current_user.id)
        if form.validate_on_submit():
            try:
                plots = request.form.getlist("plots")
                form_data = copy(form.data)

                # Get configurations from the CONTRACT_SETTINGS section of the config file
                config = ResourceManager.load_config("CONF", user.username)
                form_data["date_signed_for_generated_contracts"] = config["CONTRACT_SETTINGS"]["datesigned"]
                form_data["date_started_for_generated_contracts"] = config["CONTRACT_SETTINGS"]["datestarted"]
                form_data["kg_per_dka_for_generated_contracts"] = config["CONTRACT_SETTINGS"]["kgperdkaincontract"]

                ContractChannel.add_contract(owner_id, plots, **form_data)

                flash('Договорът е успешно добавен', 'add_contract_msg')
                return redirect(url_for('contracts'))
            except ValueError as inst:
                return cls.render_contracts_page()  # Must not have selected any plots
            except Exception as inst:
                traceback.print_exc()
                db.session.rollback()
        else:
            app.logger.error(form.errors)
        return render_template('contracts/contracts.html', contracts=contracts, next_url=next_url, prev_url=prev_url,
                               form=form, owners=owners, localities=localities, ownerships=ownerships,
                               query=query, owner_id=owner_id)

    @classmethod
    def download_contracts(cls):
        localities = Locality.query.all()
        memory_file = BytesIO()
        with ZipFile(memory_file, 'w') as zf:
            for locality in localities:
                for contract in locality.contracts:
                    owner_names = [contract_owner.owner.name for contract_owner in contract.contract_owners]
                    filename = f"{'-'.join(owner_names)}-{contract.first_agricultural_year}.pdf"
                    data = ZipInfo(os.path.join('contracts', locality.name, filename))
                    data.date_time = time.localtime(time.time())[:6]
                    data.compress_type = ZIP_DEFLATED
                    with open(contract.doc_path, 'rb') as f:
                        zf.writestr(data, f.read())
        memory_file.seek(0)
        return send_file(memory_file, attachment_filename='contracts.zip', as_attachment=True)

    @classmethod
    def edit_contract(cls, contract_id):
        contract = Contract.query.get_or_404(contract_id)
        form = EditContractForm(obj=contract)
        if form.validate_on_submit():
            ContractChannel.edit_contract(contract, form.doc_path.data, form.notes.data)
            flash('Информацията за договора е успешно обновена', 'edit_contract_msg')
            return redirect(url_for('contract', contract_id=contract.id))
        else:
            app.logger.error(form.errors)
        return render_template('contracts/contract.html', contract=contract, form=form)

    @classmethod
    def delete_contract(cls, contract_id):
        ContractChannel.delete_contract(contract_id)
        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
