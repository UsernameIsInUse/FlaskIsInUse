from project import login
from project.views import bp
from flask import render_template, redirect, url_for, request
from flask_login import login_user, logout_user, current_user
from flask_flashy import flash
from project.models import User, Profile
from project.utils import log, db_add
from project.forms import LoginForm, RegisterForm

@login.user_loader
def load_user(id):
  return User.query.get(int(id))
  
@bp.route('/login', methods=['GET', 'POST'])
def login():
  if current_user.is_authenticated:
    flash('Already logged in!', 'info')
    return redirect(current_user.profile.url)
  form = LoginForm()
  
  if form.validate_on_submit():
    user = User.query.filter_by(email=form.email.data).first()
    if user and user.check_password(form.password.data):
      login_user(user, remember=form.remember_me.data)
      log(request=request, user=user, description='Logged In')
      next = request.args.get("next")
      return redirect(next or current_user.profile.url)
    else:
      flash('Invalid email or password. Register instead?', 'warning', url=url_for('views.register'))
      log(request=request, description='Failed login attempt')
  
  return render_template('login/login.html', form=form)
  
@bp.route('/register', methods=['GET', 'POST'])
def register():
  if current_user.is_authenticated:
    flash('Already logged in!', 'info')
    return redirect(current_user.profile.url)
  form = RegisterForm()
  
  if form.validate_on_submit():
    user = User.query.filter_by(email=form.email.data).first()
    profile = Profile.query.filter_by(username=form.username.data).first()
    if user:
      flash("Email already registered. Login?", 'warning', url=url_for('views.login'))
    if profile:
      flash("Username is in use. Login?", 'warning', url=url_for('views.login'))
    if not user and not profile:
      profile = Profile(username=form.username.data)
      db_add(profile)
      user = User(email=form.email.data, profile=profile, tos=form.tos.data)
      user.set_password(form.password.data)
      db_add(user)
      log(request=request, user=user, description='Registered')
      login_user(user)
      return redirect(current_user.profile.url)
  
  return render_template('login/register.html', form=form)
      
  
@bp.route('/logout')
def logout():
  logout_user()
  log(request=request, user=current_user, description='Logged out')
  flash('Successfully logged out!', 'success')
  return redirect(url_for('views.index'))
