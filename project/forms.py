from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, SelectMultipleField, SelectField, HiddenField, TextAreaField
from wtforms.validators import DataRequired, Length, ValidationError, EqualTo, Email, Regexp

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
                                     Email()])
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
