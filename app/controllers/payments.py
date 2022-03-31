import datetime
import json
import os
import time
import traceback
from datetime import date
from io import BytesIO
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED

from flask import render_template, redirect, flash, request
from flask.helpers import url_for, send_file
from flask_login import current_user
from sqlalchemy import distinct

from app import app, db
from app.forms import MakePaymentForm, EditPaymentForm
from app.models import Payment, Owner, ContractOwner, User, Locality
from utils import DocumentGenerator, ResourceManager
from .paginated_search_controller import PaginatedSearchController
from ..channels import PaymentChannel


class PaymentController:

    @classmethod
    def render_payments_page(cls, payment_form=None, preclicked_payment_id=None):
        if not payment_form:
            payment_form = MakePaymentForm()
        payments, next_url, prev_url, query = PaginatedSearchController.paginate(Payment, 'payments')
        owners_ids = db.session.query(distinct(ContractOwner.owner_id)).all()
        owners = Owner.query.filter(Owner.id.in_(owners_ids)).all()
        owner_data = [{"owner_id": owner.id, "owner_name": owner.name} for owner in owners]
        owners_json = json.dumps(owner_data)
        return render_template('payments/payments.html', payments=payments, next_url=next_url, prev_url=prev_url,
                               payment_form=payment_form, owners_json=owners_json, query=query,
                               preclicked_payment_id=preclicked_payment_id)

    @classmethod
    def render_payment_page(cls, payment_id):
        owners = Owner.query.all()
        owner_data = [{"owner_id": owner.id, "owner_name": owner.name} for owner in owners]
        owners_json = json.dumps(owner_data)
        payment = Payment.query.get(payment_id)
        payment_form = EditPaymentForm(obj=payment)
        if payment.doc_path:
            try:
                stored_doc_path = url_for('static', filename=payment.doc_path.split('static\\')[1].replace('\\', '/'))
            except:
                stored_doc_path = None
        else:
            stored_doc_path = None
        return render_template('payments/payment.html', payment_form=payment_form, owners_json=owners_json,
                               payment=payment, current_user=current_user, stored_doc_path=stored_doc_path)

    @classmethod
    def generate_payments(cls):
        owner_ids_for_cash_payment = request.form.getlist('owners_for_cash_payment[]')
        owner_ids_for_bank_payment = request.form.getlist('owners_for_bank_payment[]')
        user = User.query.get_or_404(current_user.id)

        config = ResourceManager.load_config("CONF", user.username)
        # Get configurations from the RENT_SETTINGS section of the config file
        rent_per_unit_of_area = float(config["RENT_SETTINGS"]["bgnperdka"])
        # Get configurations from the TEMPLATE_SETTINGS section of the config file
        agricultural_year = config["TEMPLATE_SETTINGS"]["agriculturalyear"]
        cash_payment_date = config["TEMPLATE_SETTINGS"]["cashpaymentdocdate"]
        bank_payment_date = config["TEMPLATE_SETTINGS"]["bankpaymentdocdate"]
        reason_for_bank_payment = config["TEMPLATE_SETTINGS"]["reasonforbankpayment"]

        for owner_id in owner_ids_for_cash_payment:
            PaymentChannel.generate_cash_payments(user, owner_id, rent_per_unit_of_area, agricultural_year,
                                                  cash_payment_date)
        for owner_id in owner_ids_for_bank_payment:
            PaymentChannel.generate_bank_payments(user, owner_id, rent_per_unit_of_area, agricultural_year,
                                                  bank_payment_date, reason_for_bank_payment)
        flash('Плащанията са генерирани успешно', 'generate_payment_msg')
        return cls.render_payments_page()

    @classmethod
    def download_generated_payments_docs(cls):
        localities = Locality.query.all()
        memory_file = BytesIO()
        with ZipFile(memory_file, 'w') as zf:
            for locality in localities:
                for contract in locality.contracts:
                    owner_names = [contract_owner.owner.name for contract_owner in contract.contract_owners]
                    for payment in contract.payments:
                        filename = f"{'-'.join(owner_names)}-{contract.id}-{payment.id}.pdf"
                        data = ZipInfo(os.path.join('payments', locality.name, contract.id, filename))
                        data.date_time = time.localtime(time.time())[:6]
                        data.compress_type = ZIP_DEFLATED
                        with open(payment.doc_path, 'rb') as f:
                            zf.writestr(data, f.read())
        memory_file.seek(0)
        return send_file(memory_file, attachment_filename='payments.zip', as_attachment=True)

    @classmethod
    def edit_payment(cls, payment_id):
        owners = Owner.query.all()
        owner_data = [{"owner_id": owner.id, "owner_name": owner.name} for owner in owners]
        owners_json = json.dumps(owner_data)
        payment = Payment.query.get_or_404(payment_id)
        payment_form = EditPaymentForm(obj=payment)
        payment_form.payment_type.data = 'изплащане'  # Filled in order to pass validation
        if payment_form.validate_on_submit():
            PaymentChannel.edit_payment(payment, payment_form.doc_path.data, payment_form.notes.data)
            flash('Информацията за плащането е успешно обновена', 'edit_payment_msg')
            return redirect(url_for('payment', payment_id=payment.id))
        else:
            app.logger.error(payment_form.errors)
        return render_template('payments/payment.html', payment=payment, payment_form=payment_form,
                               owners_json=owners_json)

    @classmethod
    def get_payment_data(cls, payment_id):
        payment = Payment.query.get_or_404(payment_id)
        contract = payment.contract

        config = ResourceManager.load_config("CONF", current_user.username)
        kg_per_dka = int(config['RENT_SETTINGS']['kgperdka'])
        rent_per_unit_of_area = float(config["RENT_SETTINGS"]["bgnperdka"])
        selected_grain_types = config["RENT_SETTINGS"]["selectedgraintypes"]
        selected_grain_mixers = config["RENT_SETTINGS"]["selectedgrainmixers"]
        kg_per_dka_in_contract = int(config['CONTRACT_SETTINGS']['kgperdkaincontract'])
        rent_calculation = config["RENT_SETTINGS"]["rentcalculation"]

        ownerships = [contract_subject.ownership for contract_subject in contract.contract_subjects]
        plots_array = [
            {'id': ownership.plot.id,
             'area': round(ownership.plot.area_workable * (ownership.total_owned_area / ownership.plot.area_by_doc)
                           if rent_calculation == 'ByWorkableArea' else ownership.total_owned_area, 2),
             'sublocality': ownership.plot.sublocality.name} for ownership in ownerships]

        response_data = {'payment_id': payment.id,
                         'contract_id': payment.contract_id,
                         'owner_name': payment.contract.contract_owners[0].owner.name,
                         'owner_egn': payment.contract.contract_owners[0].owner.egn,
                         'payment_date': f"{payment.date.day}.0{payment.date.month}.{payment.date.year}",
                         'kg_per_dka': kg_per_dka,
                         'kg_per_dka_in_contract': kg_per_dka_in_contract,
                         'rent_per_unit_of_area': rent_per_unit_of_area,
                         'selected_grain_types': selected_grain_types,
                         'selected_grain_mixers': selected_grain_mixers,
                         'plots': plots_array
                         }

        def datetime_to_json(o):
            if isinstance(o, datetime.date):
                return o.__str__()

        return json.dumps(response_data, default=datetime_to_json), 200, {'ContentType': 'application/json'}

    @classmethod
    def make_edit_payment(cls, payment_id):
        if 'make_payment_submit' in request.form:
            # submit from modal make payment
            payment_form = MakePaymentForm()
            if payment_form.validate_on_submit():
                try:
                    Payment.query.filter(Payment.id == payment_id).update(
                        dict(paid_amount_bgn=payment_form.paid_amount_bgn.data,
                             grain_weight=payment_form.grain_weight.data,
                             grain_type=payment_form.grain_type.data,
                             mixed_grain_weight=payment_form.mixed_grain_weight.data,
                             mixed_grain_holder=payment_form.mixed_grain_holder.data,
                             status='ИЗПЪЛНЕНО'))
                    db.session.commit()
                except Exception as inst:
                    traceback.print_exc()
                    print(inst)
                flash('Плащането е извършено успешно', 'make_payment_msg')
                return redirect(url_for('payments'))
            else:
                app.logger.error(payment_form.errors)
                return cls.render_payments_page(payment_form=payment_form, preclicked_payment_id=payment_id)
        else:
            # submit from payment single page edit
            return cls.edit_payment(payment_id)

    @classmethod
    def delete_payment(cls, payment_id):
        PaymentChannel.delete_payment(payment_id)
        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
