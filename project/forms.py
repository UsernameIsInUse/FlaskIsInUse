from flask_wtf import FlaskForm

from wtforms import StringField, SubmitField, PasswordField, BooleanField, SelectMultipleField, SelectField, HiddenField, TextAreaField
from wtforms.validators import DataRequired, Length, ValidationError, EqualTo, Email, Regexp, Optional

class LoginForm(FlaskForm):
  email = StringField('Email',
                         validators=[Optional(),
                                     Length(min=6, max=255),
                                     Email()])
  password = PasswordField('Password',
                           validators=[Optional(),
                                       Length(min=8, max=255)])
  remember_me = BooleanField("Remember Me")
  submit = SubmitField('Login')
  
class RegisterForm(FlaskForm):
  email = StringField('Email',
                         validators=[Optional(),
                                     Length(min=6, max=255),
                                     Email()])
  username = StringField('Username',
                         validators=[DataRequired(),
                                     Length(min=1, max=64),
                                     Regexp('^[A-Za-z0-9_-]+$', message="Username can only contain letters, numbers, underscores, and dashes.")])
  password = PasswordField('Password',
                           validators=[Optional(),
                                       Length(min=8, max=255)])
  password2 = PasswordField('Repeat Password',
                            validators=[Optional(),
                                        EqualTo('password')])
  tos = BooleanField("Terms of Service", validators=[DataRequired()])
  marketing = BooleanField("Marketing", validators=[Optional()])
  submit = SubmitField()

class EmailChangeForm(FlaskForm):
  email = StringField('New Email',
                         validators=[DataRequired(),
                                     Length(min=6, max=255),
                                     Email()])
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

class SubmitForm(FlaskForm):
  submit = SubmitField('Submit')