import json
import os
from copy import copy

from flask import render_template, request, redirect, flash
from flask import session
from flask.helpers import url_for
from werkzeug.datastructures import FileStorage

from app import app, db
from app.config import OBJECTS_PER_PAGE
from app.forms import AddPlotForm, EditPlotForm
from app.models import Plot, Owner, Ownership
from utils import ResourceManager
from .paginated_search_controller import PaginatedSearchController
from ..channels import PlotChannel
from ..validators import localities_json


class PlotController:

    @classmethod
    def render_plots_page(cls):
        form = AddPlotForm()
        ownerships, next_url, prev_url, query = PaginatedSearchController.paginate(Ownership, 'plots')
        owners = Owner.query.all()
        owner_id = request.args.get('owner_id')
        return render_template('plots/plots.html', ownerships=ownerships, next_url=next_url, prev_url=prev_url,
                               owners=owners, form=form, owner_id=owner_id, localities_json=localities_json,
                               query=query)

    @classmethod
    def render_plot_page(cls, ownership_id):
        ownership = Ownership.query.get_or_404(ownership_id)
        form_data = {
            'id': ownership.plot.id,
            'locality_id': '',
            'sublocality_id': '',
            'category': ownership.plot.category,
            'use_type_id': ownership.plot.use_type_id,
            'area_workable': ownership.plot.area_workable,
            'area_by_doc': ownership.plot.area_by_doc,
            'notes': ownership.plot.notes,
            'locality_name': '',
            'sublocality_name': '',
            'plot': '',
            'doc_date': ownership.doc_date,
            'doc_number': ownership.doc_number,
            'doc_path': ownership.doc_path,
            'total_owned_area': ownership.total_owned_area,
            'owned_plot_fraction_numerator': ownership.owned_plot_fraction_numerator,
            'owned_plot_fraction_denominator': ownership.owned_plot_fraction_denominator,
            'additional_owned_area': ownership.additional_owned_area,
            'area_display': ownership.plot.area_by_doc
        }
        form = EditPlotForm(data=form_data)
        if ownership.doc_path:
            try:
                stored_doc_path = url_for('static', filename=ownership.doc_path.split('static\\')[1].replace('\\', '/'))
            except:
                stored_doc_path = None
        else:
            stored_doc_path = None
        return render_template('plots/plot.html', ownership=ownership, form=form, localities_json=localities_json,
                               stored_doc_path=stored_doc_path)

    @classmethod
    def add_plot(cls):
        user_id = session.get('user_id')
        owner_id = request.args.get('owner_id', None, type=int)
        ownerships = Ownership.query.paginate(1, OBJECTS_PER_PAGE, False)
        owners = Owner.query.all()
        owner_exists = db.session.query(db.exists().where(Owner.id == owner_id)).scalar()
        form = AddPlotForm()
        if form.validate_on_submit() and owner_exists:
            PlotChannel.add_plot(user_id, owner_id, **form.data)
            form_data = {
                'id': '',
                'locality_id': '',
                'sublocality_id': '',
                'category': '',
                'use_type_id': '',
                'area_workable': '',
                'area_by_doc': '',
                'notes': '',
                'locality_name': '',
                'sublocality_name': '',
                'plot': '',
                'doc_date': '',
                'doc_number': '',
                'doc_path': '',
                'total_owned_area': '',
                'owned_plot_fraction_numerator': '',
                'owned_plot_fraction_denominator': '',
                'additional_owned_area': '',
                'area_display': ''
            }
            form = AddPlotForm(data=form_data)
            if form.add_contract_after_plot_btn.data:
                return redirect(url_for('contracts', owner_id=owner_id))
            elif form.add_multiple_plots_btn.data:
                return redirect(url_for('plots', owner_id=owner_id))
            elif form.add_single_plot_btn.data:
                return redirect(url_for('plots'))  # plots home page without preselected owner
        else:
            app.logger.error(form.errors)
        return render_template('plots/plots.html', ownerships=ownerships, owners=owners, owner_id=owner_id, form=form,
                               localities_json=localities_json)

    @classmethod
    def edit_plot(cls, ownership_id):
        ownership = Ownership.query.get_or_404(ownership_id)
        plot = Plot.query.get_or_404(ownership.plot_id)
        form = EditPlotForm()
        form.id.data = ownership.plot_id
        if form.validate_on_submit():
            form_data = copy(form.data)
            del form_data['plot']
            PlotChannel.edit_plot(plot, ownership, **form_data)
            flash('Информацията за парцела е успешно обновена', 'edit_plot_msg')
            return redirect(url_for('plot', ownership_id=ownership.id))
        else:
            app.logger.error(form.errors)
        return render_template('plots/plot.html', ownership=ownership, form=form, localities_json=localities_json)

    @classmethod
    def delete_plot(cls, ownership_id):
        PlotChannel.delete_plot(ownership_id)
        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
