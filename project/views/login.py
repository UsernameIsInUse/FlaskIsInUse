from project import login, db
from project.views import bp
from flask import render_template, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from flask_flashy import flash
from project.models import User, Profile, Group, UserGroup
from project.utils import log, db_add, send_email
from project.forms import LoginForm, RegisterForm, EmailChangeForm, EmailForm, PasswordChangeForm
from project.access_control import generate_token, confirm_token, confirmed_check_decorator, not_confirmed_check_decorator, not_authenticated_check_decorator
from datetime import datetime
from project.services import send_password_reset_email

@login.user_loader
def load_user(id):
  return User.query.get(int(id))

@login.needs_refresh_handler
def refresh():
  logout_user()
  flash("Please log in again to access this page.", 'info')
  return redirect(url_for('views.login', next=request.full_path))

@bp.route('/login', methods=['GET', 'POST'])
@confirmed_check_decorator
@not_authenticated_check_decorator
def login():
  form = LoginForm()
  if form.validate_on_submit():
    user = User.query.filter_by(email=form.email.data).first()
    if user and user.check_password(form.password.data):
      login_user(user, remember=form.remember_me.data)
      log(request=request, user=user, description='Logged In')
      next = request.args.get("next")
      #return redirect(next or current_user.profile.url)
      if not user.confirmed:
        return redirect(url_for('views.confirm'))
      return redirect(next or url_for('views.index'))
    else:
      flash('Invalid email or password. Register instead?', 'warning', url=url_for('views.register'))
      log(request=request, description='Failed login attempt')
  
  return render_template('user/login.html', form=form)
  
@bp.route('/register', methods=['GET', 'POST'])
@confirmed_check_decorator
@not_authenticated_check_decorator
def register():
  form = RegisterForm()
  if form.validate_on_submit():
    user = User.query.filter_by(email=form.email.data).first()
    profile = Profile.query.filter_by(username=form.username.data).first()
    if user or profile:
      flash("Unable to create account with those credentials.", "warning")
    if not user and not profile:
      user = User(email=form.email.data, unconfirmed_email=form.email.data, tos=form.tos.data, marketing=form.marketing.data)
      user.set_password(form.password.data)
      db_add(user)
      group = Group(name=form.username.data)
      db_add(group)
      profile = Profile(username=form.username.data, group=group, owner=user)
      db_add(profile)
      usergroup = UserGroup(user=user, group=group)
      db_add(usergroup)
      log(request=request, user=user, description='Registered')
      login_user(user)
      return redirect(url_for('views.confirm'))
  
  return render_template('user/register.html', form=form)
      
@bp.route('/logout')
@login_required
def logout():
  log(request=request, user=current_user, description='Logged out')
  logout_user()
  flash('Successfully logged out!', 'success')
  return redirect(url_for('views.index'))

@bp.route('/confirm/', methods=['GET', 'POST'])
@login_required
@not_confirmed_check_decorator
def confirm():
  form = EmailChangeForm()
  if form.validate_on_submit():
    if not User.query.filter_by(unconfirmed_email=form.email.data).first():
      current_user.unconfirmed_email = form.email.data
      db.session.commit()
  token = generate_token(current_user.unconfirmed_email)
  confirm_url = url_for("views.confirm_email", token=token, _external=True)
  html = render_template("email/email_confirmation.html", confirm_url=confirm_url, unsubscribe=False)
  subject = "Confirm Your vfolio Account"
  send_email([current_user.unconfirmed_email],subject,html)
  flash("Confirmation email sent.", 'info')
  return render_template("user/confirm.html", title="Confirm", form=form)

@bp.route('/confirm/<token>')
@not_confirmed_check_decorator
def confirm_email(token):
  email = confirm_token(token)
  try:
    user = User.query.filter_by(unconfirmed_email=email).first()
    if user.confirmed:
      flash("Email already confirmed", "info")
      return redirect(url_for('views.login'))
    else:
      user.email = user.unconfirmed_email
      user.unconfirmed_email = None
      user.confirmed = True
      user.date_confirmed = datetime.now()
      db.session.commit()
      flash("Email confirmed!",'success')
      log(request=request, user=current_user, description='Email confirmed')
      if current_user.is_authenticated:
        return redirect(url_for("views.profile_setup"))
      else:
        return redirect(url_for("views.confirm_success"))
  except:
    flash("The confirmation link is invalid or has expired.", "info")
    log(request=request, user=current_user, description='Email confirmation failed')
    return redirect(url_for("views.confirm"))

@bp.route('/confirmation/')
@confirmed_check_decorator
def confirm_success():
  return render_template("user/confirm_success.html", title="Confirm")

@bp.route('/password/forgot/', methods=['GET', 'POST'])
def password_request():
  form = EmailForm()
  return render_template("user/password_request.html", title="Forgot Password", form=form,)

@bp.route('/password/forgot/<email>')
def password_request_send(email):
  send_password_reset_email(email)
  flash("An email has been sent to reset your password.","info")
  return redirect(url_for('views.password_request'))
  
@bp.route('/password/reset/', methods=['GET', 'POST'])
def password_reset():
  return render_template("user/password_wait.html", title="Reset Password")

@bp.route('/password/reset/<token>', methods=['GET', 'POST'])
def password_reset_token(token):
  email = confirm_token(token)
  user = User.query.filter_by(email=email).first()
  form = PasswordChangeForm()
  try:
    if form.validate_on_submit():
      user.set_password(form.password.data)
      db.session.commit()
      if current_user.is_authenticated:
        logout_user()
      flash("Password reset, please log in.", "success")
      return redirect(url_for('views.login'))
    elif user:
      return render_template("user/password_reset.html", title="Reset Password", form=form)
    return render_template("user/password_reset.html", title="Reset Password", form=None)
  except Exception as e:
    flash("The reset link is invalid or has expired.", "info")
    log(request=request, user=current_user, description='Password change failed')
    return redirect(url_for("views.password_request"))
  