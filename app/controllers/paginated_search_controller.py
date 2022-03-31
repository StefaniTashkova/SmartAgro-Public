from flask import request, abort
from flask.helpers import url_for
from flask_sqlalchemy import Pagination

from app import db
from app.config import OBJECTS_PER_PAGE
from app.models import *


class PaginatedSearchController:

    @classmethod
    def _do_pagination(cls, query, page, per_page=20, error_out=True):
        if error_out and page < 1:
            abort(404)
        items = query.distinct().limit(per_page).offset((page - 1) * per_page).all()
        if not items and page != 1 and error_out:
            abort(404)

        # No need to count if we're on the first page and there are fewer
        # items than we expected.
        if page == 1 and len(items) < per_page:
            total = len(items)
        else:
            total = query.distinct().order_by(None).count()

        return Pagination(query, page, per_page, total, items)

    @classmethod
    def paginate(cls, model_class, endpoint, query_argument_name='query', page_argument_name='page'):
        page_number = request.args.get(page_argument_name, 1, type=int)
        query_param = request.args.get(query_argument_name, None, type=str)
        if not query_param:
            response = db.session.query(model_class).paginate(page_number, OBJECTS_PER_PAGE, False)
        else:
            query_string = query_param.replace('_', '\_')
            query_string = f"%{query_string}%"
            query = None
            if model_class == Owner:
                query = cls._build_owners_query(query_string)
            if model_class == Ownership:
                query = cls._build_plots_query(query_string)
            if model_class == Contract:
                query = cls._build_contracts_query(query_string)
            if model_class == Payment:
                query = cls._build_payments_query(query_string)
            # If query is None at this point you need to write a _build_XXX_query method depending on the model class
            response = cls._do_pagination(query, page_number, OBJECTS_PER_PAGE, False)  # custom pagination
        next_url = url_for(endpoint, page=response.next_num, query=query_param) if response.has_next else None
        prev_url = url_for(endpoint, page=response.prev_num, query=query_param) if response.has_prev else None
        return response, next_url, prev_url, query_param

    @classmethod
    def _build_owners_query(cls, query_string):
        query = db.session.query(Owner).filter(
            (Owner.id.like(query_string)) | (Owner.name.like(query_string)) | (Owner.egn.like(query_string)))
        return query

    @classmethod
    def _build_plots_query(cls, query_string):
        contracts = db.session.query(Contract).filter(Contract.id.like(query_string)).all()
        ownership_ids_of_matching_contracts = [subject.ownership_id for contract in contracts for subject in
                                               contract.contract_subjects]
        query = db.session.query(Ownership) \
            .join(Plot, Plot.id == Ownership.plot_id) \
            .join(Locality, Locality.id == Plot.locality_id) \
            .join(Owner, Owner.id == Ownership.owner_id) \
            .join(Sublocality, Sublocality.sublocality_code == Plot.sublocality_id) \
            .filter((Plot.id.like(query_string)) |
                    (Plot.area_by_doc.like(query_string)) |
                    (Owner.name.like(query_string)) |
                    (Locality.name.like(query_string)) |
                    (Sublocality.name.like(query_string)) |
                    (Ownership.id.in_(ownership_ids_of_matching_contracts)))
        return query

    @classmethod
    def _build_contracts_query(cls, query_string):
        query = db.session.query(Contract) \
            .join(ContractOwner, ContractOwner.contract_id == Contract.id) \
            .join(ContractType, ContractType.id_contract_type == Contract.contract_type) \
            .join(Owner, Owner.id == ContractOwner.owner_id) \
            .filter(
            (Contract.id.like(query_string)) | (ContractType.name.like(query_string)) | (
                Owner.name.like(query_string)))
        return query

    @classmethod
    def _build_payments_query(cls, query_string):
        query = db.session.query(Payment) \
            .join(Contract, Payment.contract_id == Contract.id) \
            .join(ContractOwner, ContractOwner.contract_id == Contract.id) \
            .join(Owner, Owner.id == ContractOwner.owner_id) \
            .filter((Payment.date.like(query_string)) |
                    (Payment.type.like(query_string)) |
                    (Owner.name.like(query_string)) |
                    (Payment.agricultural_year.like(query_string)) |
                    (Contract.id.like(query_string)) |
                    (Payment.status.like(query_string)))
        return query
