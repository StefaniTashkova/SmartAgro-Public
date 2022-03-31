import os

from werkzeug.datastructures import FileStorage

from app import db
from app.models import Plot, Ownership
from utils import ResourceManager
from .abtract_channel import AbstractChannel
from .contract_channel import ContractChannel


class PlotChannel(AbstractChannel):

    @classmethod
    def add_plot(cls, user_id, owner_id, id, area_by_doc, area_workable, category, use_type_id, notes,
                 owned_plot_fraction_numerator, owned_plot_fraction_denominator, additional_owned_area, doc_number,
                 doc_date, doc_path, *args, **kwargs):
        plot = Plot.query.filter_by(id=id).first()
        if plot is None:
            # must add plot first
            locality_id, sublocality_id, _ = id.split('.')
            plot = Plot(id=id,
                        area_by_doc=area_by_doc,
                        area_workable=area_workable if area_workable else area_by_doc,
                        category=category,
                        locality_id=locality_id,
                        sublocality_id=int(sublocality_id),
                        use_type_id=use_type_id,
                        notes=notes)
            db.session.add(plot)
        total_owned_area = cls._calculate_total_owned_area(area_by_doc, owned_plot_fraction_numerator,
                                                           owned_plot_fraction_denominator,
                                                           additional_owned_area)
        local_path = ResourceManager.save_resource('ownership_docs', doc_path)

        ownership = Ownership(
            user_id=user_id,
            plot_id=plot.id,
            owner_id=owner_id,
            total_owned_area=total_owned_area,
            owned_plot_fraction_numerator=owned_plot_fraction_numerator,
            owned_plot_fraction_denominator=owned_plot_fraction_denominator,
            additional_owned_area=additional_owned_area,
            doc_number=doc_number,
            doc_date=doc_date,
            doc_path=local_path
        )
        cls.add_objects([plot, ownership])
        return plot, ownership

    @classmethod
    def edit_plot(cls, plot: Plot, ownership: Ownership, area_by_doc, area_workable, category, use_type_id, notes,
                  owned_plot_fraction_numerator, owned_plot_fraction_denominator, additional_owned_area, doc_number,
                  doc_date, doc_path, *args, **kwargs):
        old_path = ownership.doc_path
        doc_path_changed = True if isinstance(doc_path, FileStorage) else False
        if doc_path_changed:
            local_path = ResourceManager.save_resource('ownership_docs', doc_path)
            ownership.doc_path = local_path
        total_owned_area = cls._calculate_total_owned_area(area_by_doc, owned_plot_fraction_numerator,
                                                           owned_plot_fraction_denominator,
                                                           additional_owned_area)
        ownership.total_owned_area = total_owned_area,
        ownership.owned_plot_fraction_numerator = owned_plot_fraction_numerator
        ownership.owned_plot_fraction_denominator = owned_plot_fraction_denominator
        ownership.additional_owned_area = additional_owned_area
        ownership.doc_number = doc_number
        ownership.doc_date = doc_date
        plot.area_by_doc = area_by_doc
        plot.area_workable = area_workable
        plot.category = category
        plot.use_type_id = use_type_id
        plot.notes = notes
        db.session.commit()
        if doc_path_changed:
            try:
                os.remove(old_path)
            except:
                pass

    @classmethod
    def delete_plot(cls, ownership_id):
        ownership = Ownership.query.get(ownership_id)
        if ownership:
            for contract_subject in ownership.contract_subjects:
                ContractChannel.delete_contract(contract_subject.contract_id)
            if os.path.exists(ownership.doc_path):
                os.remove(ownership.doc_path)
            plot = ownership.plot
            delete_plot = True if len(plot.ownerships) == 1 else False
            db.session.delete(ownership)
            if delete_plot:
                # This is the last ownership for the plot, so we can delete the plot as well
                db.session.delete(plot)
            db.session.commit()

    @classmethod
    def _calculate_total_owned_area(cls, area_by_doc, owned_plot_fraction_numerator, owned_plot_fraction_denominator,
                                    additional_owned_area):
        return float(area_by_doc) * int(owned_plot_fraction_numerator) / int(owned_plot_fraction_denominator) + float(
            additional_owned_area)
