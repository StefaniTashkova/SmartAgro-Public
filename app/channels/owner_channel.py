from app import db
from app.models import Owner
from .abtract_channel import AbstractChannel
from .plot_channel import PlotChannel


class OwnerChannel(AbstractChannel):

    @classmethod
    def add_owner(cls, owner_type, name, egn, phone, nationalID_number, nationalID_issued_by, nationalID_issue_date,
                  IBAN, BIC, email, address, payment_location, notes,
                  company_name=None, company_number=None, vat_number=None, *args, **kwargs):
        owner = Owner(owner_type=owner_type,
                      name=name,
                      egn=egn,
                      phone=phone,
                      company_name=company_name,
                      company_number=company_number,
                      vat_number=vat_number,
                      nationalID_number=nationalID_number,
                      nationalID_issued_by=nationalID_issued_by,
                      nationalID_issue_date=nationalID_issue_date,
                      IBAN=IBAN,
                      BIC=BIC,
                      email=email if email else None,
                      address=address,
                      payment_location=payment_location,
                      notes=notes)
        cls.add_object(owner)
        return owner

    @classmethod
    def edit_owner(cls, owner: Owner, owner_data):
        saved_owner_type = owner.owner_type
        for key, value in owner_data.items():
            if hasattr(owner, key):
                setattr(owner, key, value)
        owner.owner_type = saved_owner_type
        db.session.commit()

    @classmethod
    def delete_owner(cls, owner_id):
        owner = Owner.query.get(owner_id)
        if owner:
            for ownership in owner.ownerships:
                PlotChannel.delete_plot(ownership.id)
            db.session.delete(owner)
            db.session.commit()
