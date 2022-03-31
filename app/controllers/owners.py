import json
from flask import render_template, redirect, flash
from flask.helpers import url_for

from app import app, db
from app.config import OBJECTS_PER_PAGE
from app.forms import AddOwnerForm, EditOwnerForm, MakePaymentForm
from app.models import Owner, OwnerType, Ownership, ContractOwner
from .paginated_search_controller import PaginatedSearchController
from ..channels import OwnerChannel


class OwnerController:

    @classmethod
    def render_owners_page(cls):
        form = AddOwnerForm()
        payment_form = MakePaymentForm()
        owners, next_url, prev_url, query = PaginatedSearchController.paginate(Owner, 'owners')
        return render_template('owners/owners.html', form=form, payment_form=payment_form, owners=owners,
                               next_url=next_url, prev_url=prev_url,
                               query=query)

    @classmethod
    def render_owner_page(cls, owner_id):
        owner = Owner.query.get(owner_id)
        form = EditOwnerForm(obj=owner)
        # owner_ownerships = Ownership.query.filter(Ownership.owner.has(id=owner_id)).all()
        owner_ownerships = Ownership.query.filter(Ownership.owner_id == owner_id).all()

        return render_template('owners/owner.html', owner=owner, form=form, owner_ownerships=owner_ownerships)

    @classmethod
    def add_owner(cls):
        form = AddOwnerForm()
        payment_form = MakePaymentForm()
        owner_type = OwnerType[form.owner_type.data] if form.owner_type.data is not None else None
        owners = Owner.query.paginate(1, OBJECTS_PER_PAGE, False)
        if form.validate_on_submit():
            exists = Owner.query.filter_by(egn=form.egn.data).scalar() is not None
            if exists:
                return render_template('owners/owners.html', owners=owners, form=form,
                                       preselected_owner_type=owner_type, user_exists=True)
            else:
                owner = OwnerChannel.add_owner(**form.data)
                return redirect(url_for('plots', owner_id=owner.id))
        else:
            app.logger.error(form.errors)
        return render_template('owners/owners.html', owners=owners, form=form,payment_form=payment_form,
                               preselected_owner_type=owner_type)

    @classmethod
    def edit_owner(cls, owner_id):
        owner = Owner.query.get_or_404(owner_id)
        form = EditOwnerForm()
        if form.validate_on_submit():
            OwnerChannel.edit_owner(owner, form.data)
            flash('Информацията за собственика е успешно обновена', 'edit_owner_msg')
            return redirect(url_for('owner', owner_id=owner.id))
        else:
            app.logger.error(form.errors)
        return render_template('owners/owner.html', owner=owner, form=form)

    @classmethod
    def delete_owner(cls, owner_id):
        OwnerChannel.delete_owner(owner_id)
        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
