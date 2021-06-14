from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, PasswordField, BooleanField, FloatField
from wtforms.validators import DataRequired, ValidationError, EqualTo
import app


class RegistrationForm(FlaskForm):
    name = StringField('Name', [DataRequired()])
    surname = StringField('Surname', [DataRequired()])
    email = StringField('Email', [DataRequired()])
    password = PasswordField('Password', [DataRequired()])
    password_check = PasswordField('Please re-enter password', [EqualTo('password', 'Passwords must match')])
    submit = SubmitField('Submit data')


    def check_name(self, name):
        user = app.User.query.filter_by(name=name.data).first()
        if user:
            raise ValidationError('Such user is already exists')

    def check_email(self, email):
        user = app.User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('This email is already registered')


class LoginForm(FlaskForm):
    email = StringField('Email', [DataRequired()])
    password = PasswordField('Password', [DataRequired()])
    rememberme = BooleanField('Remember me')
    submit = SubmitField('Login')


class AddForm(FlaskForm):
    territory = StringField('Territory', [DataRequired()])
    placetogo = StringField('Place to go', [DataRequired()])
    description = StringField('Description', [DataRequired()])
    submit = SubmitField('Add location')




