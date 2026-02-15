from project import login, db
from project.views import bp
from flask import render_template, redirect, url_for, request, current_app, session
from flask_login import login_user, logout_user, current_user, login_required
from flask_flashy import flash
from project.models import User, Profile
from project.utils import log, db_add, send_email
from project.common.censor import check_censor
from project.forms import LoginForm, RegisterForm, EmailChangeForm, EmailForm, PasswordChangeForm
from project.access_control import generate_token, confirm_token, confirmed_check_decorator, not_confirmed_check_decorator, not_authenticated_check_decorator, validate_turnstyle, login_redirect
from project.services import setup_user, send_password_reset_email, send_email_confirmation_email
from datetime import datetime
from project.extensions import ipban

@login.user_loader
def load_user(id):
  return User.query.get(int(id))

@login.needs_refresh_handler
def refresh():
  logout_user()
  flash("Please log in again to access this page.", 'info')
  return login_redirect()

@bp.route('/login', methods=['GET', 'POST'])
@confirmed_check_decorator
@not_authenticated_check_decorator
def login():
  form = LoginForm()
  if form.validate_on_submit():
    
    # Check Honeypot
    honeypot = request.form.get('username')
    if not honeypot:
      ipban.add()
      flash('Something went wrong. Use another login method or register instead?', 'warning', url=url_for('views.register'))
      log(request=request, description='Failed login attempt, tripped honeypot')
      form = LoginForm()
      return render_template('user/login.html', form=form, ts_site_key=current_app.config["TURNSTILE_SITE_KEY"])
    
    login_type = request.form.get('submit')
    
    if login_type == "local":
    
      user = User.query.filter_by(email=form.email.data).first()
      if user and user.hashed_pass:
        if user.check_password(form.password.data):
          login_user(user, remember=form.remember_me.data)
          log(request=request, user=user, description='Logged in via local auth')
          next = request.args.get("next")
          #return redirect(next or current_user.profile.url)
          if not user.confirmed:
            return redirect(url_for('views.confirm'))
          return redirect(next or url_for('views.index'))
        else:
          flash('Something went wrong. Use another login method or register instead?', 'warning', url=url_for('views.register'))
          log(request=request, description='Failed login attempt, likely wrong password')
      else:
        flash('Something went wrong. Use another login method or register instead?', 'warning', url=url_for('views.register'))
        log(request=request, description='Failed login attempt, no local password found')
    
    else:
      session["oauth_type"] = "login"
      return redirect(url_for('views.login_oauth', provider=login_type)) 
    
  return render_template('user/login.html', form=form, ts_site_key=current_app.config["TURNSTILE_SITE_KEY"])
  
@bp.route('/register', methods=['GET', 'POST'])
@confirmed_check_decorator
@not_authenticated_check_decorator
def register():
  form = RegisterForm()
  if form.validate_on_submit():
    
    # Cloudflare Turnstile
    token = request.form.get('cf-turnstile-response')
    remoteip = request.headers.get('CF-Connecting-IP') or \
               request.headers.get('X-Forwarded-For') or \
               request.remote_addr
    validation = validate_turnstyle(token, current_app.config["TURNSTILE_SECRET_KEY"], remoteip=remoteip)
    if not validation['success']:
      flash('Something went wrong, please try again.', category='danger')
      log(request=request, description='Failed register attempt via turnstile verification fail')
      return render_template('user/register.html', form=form, ts_site_key=current_app.config["TURNSTILE_SITE_KEY"])
    
    # Check Honeypot
    honeypot = request.form.get('phone')
    if not honeypot:
      ipban.add()
      flash('Something went wrong. Use another login method or register instead?', 'warning', url=url_for('views.register'))
      log(request=request, description='Failed login attempt, tripped honeypot')
      form = LoginForm()
      return render_template('user/login.html', form=form, ts_site_key=current_app.config["TURNSTILE_SITE_KEY"])
    
    # Check if username is registered or censored
    profile = Profile.query.filter_by(username=form.username.data).first()
    if profile or check_censor(form.username.data):
      flash("Unable to create account with those credentials.", "warning")
      return render_template('user/register.html', form=form, ts_site_key=current_app.config["TURNSTILE_SITE_KEY"])
    
    register_type = request.form.get('submit')
    
    if register_type == "local":
      
      # Check if email, password, and password2 exist:
      if not form.email.data or not form.password.data or not form.password2.data:
        flash("Missing required credentials.", "warning")
        return render_template('user/register.html', form=form, ts_site_key=current_app.config["TURNSTILE_SITE_KEY"])
      
      # Check if email is registered
      user = User.query.filter_by(email=form.email.data).first()
      if user:
        flash("Unable to create account with those credentials.", "warning")
        return render_template('user/register.html', form=form, ts_site_key=current_app.config["TURNSTILE_SITE_KEY"])
      
      # Register and set up user
      user = User(email=form.email.data, unconfirmed_email=form.email.data, tos=form.tos.data, marketing=form.marketing.data)
      user.set_password(form.password.data)
      db_add(user)
      log(request=request, user=user, description='Registered via local auth')
      setup_user(user,form.username.data)
      login_user(user)
      return redirect(url_for('views.confirm'))
    
    else:
      session["temp_username"] = form.username.data
      session["oauth_type"] = "register"
      session["marketing"] = form.marketing.data
      return redirect(url_for('views.login_oauth', provider=register_type, username=form.username.data))
  return render_template('user/register.html', form=form, ts_site_key=current_app.config["TURNSTILE_SITE_KEY"])
      
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
  return render_template("user/confirm.html", title="Confirm", form=form)

@bp.route('/confirm/<token>')
@not_confirmed_check_decorator
def confirm_email(token):
  email = confirm_token(token)
  try:
    user = User.query.filter_by(unconfirmed_email=email).first()
    if user.confirmed:
      flash("Email already confirmed", "info")
      return login_redirect(next=False)
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
      return login_redirect(next=False)
    elif user:
      return render_template("user/password_reset.html", title="Reset Password", form=form)
    return render_template("user/password_reset.html", title="Reset Password", form=None)
  except Exception as e:
    flash("The reset link is invalid or has expired.", "info")
    log(request=request, user=current_user, description='Password change failed')
    return redirect(url_for("views.password_request"))
  