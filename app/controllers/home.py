from flask import render_template, request, redirect, flash, session
from flask.helpers import url_for
from flask_login import login_user, logout_user
from flask_mail import Message

from app import mail
from app.forms import LoginForm, ContactForm
from app.models import User


class HomeController:

    @classmethod
    def render_home_page(cls):
        login_form = LoginForm()
        contact_form = ContactForm()
        return render_template('home.html', login_form=login_form, contact_form=contact_form)

    @classmethod
    def login_or_contact(cls):
        if 'submit_contact' in request.form:
            return cls.contact()
        else:
            return cls.login()

    @classmethod
    def login(cls):
        login_form = LoginForm()
        contact_form = ContactForm()
        if login_form.validate_on_submit():
            user = User.query.filter_by(username=login_form.username.data).first()
            if user and user.check_password(login_form.password.data):
                login_user(user, remember=login_form.remember_me.data)
                session['user_id'] = user.id
                return redirect('/owners')
            else:
                flash('Invalid username or password', 'login_msg')
                return redirect(url_for('home', _anchor="home"))

        return render_template('home.html', login_form=login_form, contact_form=contact_form)

    @classmethod
    def logout(cls):
        logout_user()
        session['user_id'] = None
        return redirect(url_for('home'))

    @classmethod
    def contact(cls):
        login_form = LoginForm()
        contact_form = ContactForm()
        if contact_form.validate_on_submit():
            try:
                with mail.connect() as conn:
                    sender_name = contact_form.name.data
                    sender_email = contact_form.email.data
                    message = contact_form.message.data
                    subject_key = contact_form.subject.data
                    subject_value = dict(contact_form.subject.choices)[subject_key]
                    msg = Message(subject_value, body=message, sender=(sender_name, sender_email),
                                  recipients=['7eee6f8822-c2b2ae@inbox.mailtrap.io'])
                    conn.send(msg)
                    flash('Имейлът е изпратен успешно', 'contact_msg')
                    return redirect(url_for('home', _anchor="contact"))
            except:
                flash('Имейлът не е изпратен успешно', 'contact_msg')
                return redirect('/')

        return render_template('home.html', login_form=login_form, contact_form=contact_form, scroll='contact')
