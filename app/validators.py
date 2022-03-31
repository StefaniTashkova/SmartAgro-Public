import json

import egn
import pandas as pd
import vatnumber
from schwifty import IBAN
from wtforms.validators import DataRequired, Email, Length, Optional, Regexp, AnyOf, ValidationError

from app.models import Locality, Sublocality
from . import db
import re


def validate_egn(form, field):
    if not egn.validate(field.data):
        raise ValidationError('Невалидно ЕГН')


def validate_iban(form, field, bic_field_name='BIC'):
    bic = getattr(form, bic_field_name).data
    iban = IBAN(field.data)
    iban.validate()
    if not iban.bank_code == bic[:4]:
        raise ValidationError('Моля изберете BIC от менюто,който съвпада с посочения IBAN')


def validate_eik(form, field):
    if not hasattr(form, 'owner_type'):
        return
    if form.owner_type.data != 'юридическо лице':
        return
    if not field.data:
        return

    eik = field.data

    def get_checksum(weights, digits):
        checksum = sum([weight * digit for weight, digit in zip(weights, digits)])
        return checksum % 11

    def check_eik_base(eik):
        checksum = get_checksum(range(1, 9), eik)
        if checksum == 10:
            checksum = get_checksum(range(3, 11), eik)
        return eik[-1] == checksum % 10

    def check_eik_extra(eik):
        digits = eik[9:13]
        checksum = get_checksum([2, 7, 3, 5], digits)
        if checksum == 10:
            checksum = get_checksum([4, 9, 5, 7], digits)
        return digits[-1] == checksum % 10

    try:
        eik = list(map(int, eik))
    except ValueError:
        raise ValidationError('Моля въведете само цифри')

    if not (len(eik) in [9, 13] and check_eik_base(eik)):
        raise ValidationError('Невалиден булстат')

    if len(eik) == 13 and not check_eik_extra(eik):
        raise ValidationError('Невалиден булстат')


def validate_vat(form, field):
    if form.owner_type.data != 'юридическо лице':
        return
    if not field.data:
        return
    vat_number = field.data
    is_valid = vatnumber.check_vat(vat_number)
    if not is_valid:
        raise ValidationError('Невалиден ДДС номер')


def company_required_field(form, field):
    if form.owner_type.data == 'юридическо лице' and not field.data:
        raise ValidationError('The field is required')


def validate_area_workable(form, field):
    if form.area_workable.data > form.area_by_doc.data:
        raise ValidationError('Използваемата площ трябва да е по-малка или равна на площта по документ')


def init_locality_lookup_objects():
    join_query = Sublocality.query.join(Locality, (Sublocality.locality_id == Locality.id)).add_columns(Locality.name)
    localities_df = pd.read_sql(join_query.statement, db.session.bind)
    localities_df.columns = ['id', 'sublocality_id', 'sublocality_name', 'locality_id', 'locality_name']
    localities = {}
    for _, record in localities_df.iterrows():
        if record['locality_id'] not in localities:
            localities[record['locality_id']] = (record['locality_name'], {})
        localities[record['locality_id']][1][record['sublocality_id']] = record['sublocality_name']
    return localities, json.dumps(localities)


localities_dict, localities_json = init_locality_lookup_objects()


def validate_plot_id(form, field):
    input_split = field.data.split('.')
    if len(input_split) != 3:
        raise ValidationError('Невалиден идентификатор на имота, моля използвайте формат ЕКАТТЕ.район.имот')
    locality_id, sublocality_id, plot_id = input_split[0], input_split[1], input_split[2]
    if locality_id not in localities_dict:
        raise ValidationError('Неразпознато ЕКАТТЕ')
    if sublocality_id not in localities_dict[locality_id][1]:
        raise ValidationError('Неразпозната местност за избраното землище')
    try:
        int(plot_id)
    except:
        raise ValidationError('Имотният идентификатор е цяло число')

def validate_total_owned_area(form,field,owned_plot_fraction_numerator_name='owned_plot_fraction_numerator',owned_plot_fraction_denominator_name='owned_plot_fraction_denominator', area_by_doc_name='area_by_doc',additional_owned_area_name='additional_owned_area' ):
    owned_plot_fraction_numerator = int(getattr(form, owned_plot_fraction_numerator_name).data)
    owned_plot_fraction_denominator = int(getattr(form, owned_plot_fraction_denominator_name).data)
    area_by_doc = float(getattr(form, area_by_doc_name).data)
    additional_owned_area = float(getattr(form, additional_owned_area_name).data)
    total_owmed_area = (owned_plot_fraction_numerator/owned_plot_fraction_denominator)*area_by_doc + additional_owned_area
    if not 0 <= owned_plot_fraction_numerator/owned_plot_fraction_denominator <= 1:
        raise ValidationError('Числителят трябва да е по-малък от знаменателя')
    if total_owmed_area > area_by_doc:
        raise ValidationError('Общата притежавана площ не може да превишава общата площ по документ')

def validate_filename(form, field):
    if isinstance(field.data, str):
        filename = field.data
    else:
        filename = field.data.filename
    match = re.match('^.+\.pdf$', filename)
    if not match:
        raise ValidationError('Моля качете pdf формат')
