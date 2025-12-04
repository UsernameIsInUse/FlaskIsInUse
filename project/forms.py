from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, SelectMultipleField, SelectField, HiddenField, TextAreaField
from wtforms.validators import DataRequired, Length, ValidationError, EqualTo, Email, Regexp
from project.models import User
from flask_login import current_user

class Unique(object):
  def __init__(self, model, field, message='Email must not be in use'):
    self.model = model
    self.field = field

  def __call__(self, form, field):
    if not field.raw_data:
      check = self.model.query.filter(self.field == field.data).first()
      if check:
        raise ValidationError(self.message)

class LoginForm(FlaskForm):
  email = StringField('Email',
                         validators=[DataRequired(),
                                     Length(min=6, max=255),
                                     Email()])
  password = PasswordField('Password',
                           validators=[DataRequired(),
                                       Length(min=8, max=255)])
  remember_me = BooleanField("Remember Me")
  submit = SubmitField('Login')
  
class RegisterForm(FlaskForm):
  email = StringField('Email',
                         validators=[DataRequired(),
                                     Length(min=6, max=255),
                                     Email(),
                                     Unique(User,User.email)])
  username = StringField('Username',
                         validators=[DataRequired(),
                                     Length(min=1, max=64),
                                     Regexp('^[A-Za-z0-9_-]+$', message="Username can only contain letters, numbers, underscores, and dashes.")])
  password = PasswordField('Password',
                           validators=[DataRequired(),
                                       Length(min=8, max=255)])
  password2 = PasswordField('Repeat Password',
                            validators=[DataRequired(),
                                        EqualTo('password')])
  tos = BooleanField("Terms of Service", validators=[DataRequired()])
  submit = SubmitField('Register')

class EmailChangeForm(FlaskForm):
  email = StringField('New Email',
                         validators=[DataRequired(),
                                     Length(min=6, max=255),
                                     Email(),
                                     Unique(User,User.email)])
  submit = SubmitField('Submit')

class EmailForm(FlaskForm):
  email = StringField('Email',
                         validators=[DataRequired(),
                                     Length(min=6, max=255),
                                     Email()])

class PasswordChangeForm(FlaskForm):
  password = PasswordField('Password',
                           validators=[DataRequired(),
                                       Length(min=8, max=255)])
  password2 = PasswordField('Repeat Password',
                            validators=[DataRequired(),
                                        EqualTo('password')])
  submit = SubmitField('Submit')