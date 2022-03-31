from flask import render_template, request, redirect, flash
from flask.helpers import url_for
from flask_login import current_user

from app import app, db
from app.forms import EditUserForm
from app.models import User
from utils import ResourceManager


class UserController:

    @classmethod
    def render_settings_page(cls):
        user = User.query.filter(User.id == current_user.id).first()
        user_form = EditUserForm(obj=user)
        config = ResourceManager.load_config("CONF", user.username)
        rent_settings = dict(config.items('RENT_SETTINGS'))
        contract_settings = dict(config.items('CONTRACT_SETTINGS'))
        template_settings = dict(config.items('TEMPLATE_SETTINGS'))
        return render_template('/users/settings.html', user_form=user_form, user=user, rent_settings=rent_settings,
                               contract_settings=contract_settings, template_settings=template_settings)

    @classmethod
    def edit_user(cls):
        user = User.query.get_or_404(current_user.id)
        user_form = EditUserForm()
        config = ResourceManager.load_config("CONF", user.username)
        rent_settings = dict(config.items('RENT_SETTINGS'))
        contract_settings = dict(config.items('CONTRACT_SETTINGS'))
        template_settings = dict(config.items('TEMPLATE_SETTINGS'))
        if user_form.validate_on_submit():
            user_form.populate_obj(user)
            db.session.commit()
            flash('Информацията за стопанството е успешно обновена', 'edit_user_msg')
            return redirect(url_for('settings', _anchor="user_settings"))
        else:
            app.logger.error(user_form.errors)
        return render_template('users/settings.html', user=user, user_form=user_form,rent_settings=rent_settings,
                               contract_settings=contract_settings, template_settings=template_settings)

    @classmethod
    def edit_rent_settings(cls):
        user = User.query.get_or_404(current_user.id)
        configuration_data = request.form.copy()
        configuration_data.pop('submit')
        ResourceManager.save_config("CONF", user.username, 'RENT_SETTINGS', configuration_data)
        flash('Информацията e успешно обновена', 'update_settings_msg')
        return redirect(url_for('settings'))

    @classmethod
    def edit_contract_settings(cls):
        user = User.query.get_or_404(current_user.id)
        configuration_data = request.form.copy()
        configuration_data.pop('submit')
        ResourceManager.save_config("CONF", user.username, 'CONTRACT_SETTINGS', configuration_data)
        flash('Информацията e успешно обновена', 'update_settings_msg')
        return redirect(url_for('settings'))

    @classmethod
    def edit_template_settings(cls):
        user = User.query.get_or_404(current_user.id)
        configuration_data = request.form.copy()
        configuration_data.pop('submit')
        ResourceManager.save_config("CONF", user.username, 'TEMPLATE_SETTINGS', configuration_data)
        flash('Информацията e успешно обновена', 'update_settings_msg')
        return redirect(url_for('settings'))
