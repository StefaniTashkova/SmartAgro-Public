from flask_wtf import FlaskForm
from wtforms import (BooleanField, DateTimeField, PasswordField, SelectField,
                     StringField, SubmitField, TextAreaField, RadioField, DecimalField, FileField)
from wtforms.fields import html5 as h5fields
from wtforms.widgets import html5 as h5widgets
from flask_wtf.file import FileField, FileRequired

from app.models import Bank
from app.models import ContractType
from app.models import OwnerType
from app.models import PlotUseType
from .validators import *


class LoginForm(FlaskForm):
    username = StringField('Потребителско име', validators=[DataRequired()])
    password = PasswordField('Парола', validators=[DataRequired()])
    remember_me = BooleanField()
    submit_login = SubmitField('Вход')


class ContactForm(FlaskForm):
    name = StringField('Име', validators=[DataRequired()])
    email = StringField('Имейл', validators=[DataRequired(), Email(message='Моля въведете коректен имейл')])
    subject = SelectField('Тема', choices=[('subject', 'Избери тема'), ('service', 'Клиентско обслужване'),
                                           ('suggestions', 'Предложения'), ('product', 'Поддръжка на продукт')],
                          validators=[DataRequired()])
    message = TextAreaField('Съобщение',
                            validators=[DataRequired(), Length(min=20, message="Моля въведете поне 20 символа"),
                                        Length(max=500, message="Моля въведете до 500 символа")])
    submit_contact = SubmitField('Изпрати')


class FormFactory():
    @classmethod
    def make(cls, form_name, form_fields):
        return type(form_name, (FlaskForm,), form_fields)


user_fields = {
    'company_name': StringField(validators=[DataRequired()]),
    'company_number': StringField(validators=[DataRequired(), validate_eik]),
    'responsibleperson_name': StringField(
        validators=[DataRequired(), Regexp('^[а-яА-Я\s]*$', message='Моля въведете името на кирилица')]),
    'responsibleperson_egn': StringField(validators=[DataRequired(), validate_egn]),
    'responsibleperson_id_number': StringField(
        validators=[DataRequired(), Regexp('^[0-9]{9}$', message="Моля въведете валиден номер на ЛК")]),
    'IBAN': StringField(validators=[DataRequired(), validate_iban]),
    'BIC': SelectField(
        choices=[('', 'BIC')] + [(row.id_bic, row.id_bic) for row in Bank.query.with_entities(Bank.id_bic)],
        validate_choice=False),
}

owner_fields = {
    'owner_type': RadioField(choices=[(owner_type.name, owner_type.value) for owner_type in OwnerType],
                             validate_choice=False),
    'company_name': StringField(validators=[company_required_field]),
    'company_number': StringField(validators=[company_required_field, validate_eik]),
    'vat_number': StringField(validators=[company_required_field, validate_vat]),
    'name': StringField(
        validators=[DataRequired(), Regexp('^[а-яА-Я\s]*$', message='Моля въведете името на кирилица')]),
    'egn': StringField(validators=[DataRequired(), validate_egn]),
    'phone': StringField(validators=[DataRequired(), Regexp('^(\+359|0)\s?(([0-9]\s?){9})$',
                                                            message="Моля въведете валиден формат за телефонен номер")]),
    'nationalID_number': StringField(
        validators=[Optional(), Regexp('^[0-9]{9}$', message="Моля въведете валиден номер на ЛК")]),
    'nationalID_issue_date': DateTimeField(validators=[Optional()], format='%d/%m/%Y'),
    'nationalID_issued_by': StringField(
        validators=[Optional(), Regexp('^[а-яА-Я\s]*$', message='Моля въведете името на кирилица')]),
    'email': StringField(validators=[Optional(), Email(message='Моля въведете коректен имейл')]),
    'address': StringField(),
    'IBAN': StringField(validators=[Optional(), validate_iban]),
    'BIC': SelectField(
        choices=[('', 'BIC')] + [(row.id_bic, row.id_bic) for row in Bank.query.with_entities(Bank.id_bic)],
        validate_choice=False),
    'payment_location': SelectField(
        choices=[('', 'Място за получаване на рента'), ('Чарган', 'Чарган'), ('Търнава', 'Търнава'),
                 ('Могила', 'Могила')], validate_choice=False),
    'notes': TextAreaField()
}

plot_fields = {
    'id': StringField(validators=[DataRequired(), validate_plot_id]),
    'locality_id': StringField(),
    'sublocality_id': StringField(),
    'category': SelectField(
        choices=[('', 'Категория'), ('1', 'I'), ('2', 'II'),
                 ('3', 'III'), ('4', 'IV')]),
    'use_type_id': SelectField(
        choices=[('', 'НТП')] + [(row.id_use_type_code, row.use_type) for row in PlotUseType.query.all()],
        validate_choice=False),
    'area_workable': DecimalField(),
    'area_by_doc': DecimalField(rounding=3, validators=[DataRequired()]),
    'notes': TextAreaField(),
    'locality_name': StringField(),
    'sublocality_name': StringField(),
    'plot': StringField(),
    'doc_date': DateTimeField(format='%d/%m/%Y', validators=[DataRequired()]),
    'doc_number': StringField(validators=[DataRequired()]),
    'doc_path': FileField('Качване на файл', validators=[Optional(), validate_filename]),
    'total_owned_area': DecimalField(rounding=3, validators=[Optional(), validate_total_owned_area]),
    'owned_plot_fraction_numerator': DecimalField(validators=[DataRequired()]),
    'owned_plot_fraction_denominator': DecimalField(validators=[DataRequired()]),
    'additional_owned_area': DecimalField(rounding=3),
    'area_display': StringField(),
    'add_single_plot_btn': SubmitField('Потвърди и излез'),
    'add_multiple_plots_btn': SubmitField('Потвърди и въведи друг'),
    'add_contract_after_plot_btn': SubmitField('Потвърди и добави договор')
}

contract_fields = {
    'contract_type': RadioField(
        choices=[(contract_type.id_contract_type, contract_type.name) for contract_type in ContractType.query.all()],
        validate_choice=False, validators=[DataRequired()]),
    'date_signed': DateTimeField(format='%d/%m/%Y', validators=[DataRequired()]),
    'date_started': DateTimeField(format='%d/%m/%Y', validators=[DataRequired()]),
    'duration_years': h5fields.IntegerField(widget=h5widgets.NumberInput(min=1, max=10), validators=[DataRequired()]),
    'locality_id': SelectField(
        choices=[('', 'Място на сключване')] + [(row.id, f"{row.name}, {row.municipality}, {row.region}") for row in
                                                Locality.query.all()], validate_choice=False),
    'notes': TextAreaField(),
    'add_contract_btn': SubmitField('Потвърди'),
    'doc_path': FileField('Качване на файл', validators=[Optional(), validate_filename]),
}

payment_fields = {
    'payment_type': RadioField(
        choices=[('изплащане', 'изплащане'), ('натура', 'в натура')], validators=[DataRequired()]),
    'grain_type': SelectField(
        choices=[('', 'Вид зърно')], validate_choice=False),
    'mixed_grain_holder': SelectField(
        choices=[('', 'Смески при...')], validate_choice=False),
    'grain_weight': DecimalField(validators=[Optional()]),
    'mixed_grain_weight': DecimalField(validators=[Optional()]),
    'paid_amount_bgn': DecimalField(),
    'notes': TextAreaField(),
    'doc_path': FileField('Качване на файл', validators=[]),

}

EditUserForm = FormFactory.make('EditUserForm', user_fields)

AddOwnerForm = FormFactory.make('AddOwnerForm', owner_fields)
EditOwnerForm = FormFactory.make('EditOwnerForm', owner_fields)

AddPlotForm = FormFactory.make('AddPlotForm', plot_fields)
EditPlotForm = FormFactory.make('EditPlotForm', plot_fields)

AddContractForm = FormFactory.make('AddContractForm', contract_fields)
EditContractForm = FormFactory.make('EditContractForm', contract_fields)

MakePaymentForm = FormFactory.make('MakePaymentForm', payment_fields)
EditPaymentForm = FormFactory.make('EditPaymentForm', payment_fields)
