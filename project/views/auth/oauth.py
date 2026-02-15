from project import login, db, oauth
from project.views import bp
from flask import render_template, redirect, url_for, request, current_app, session, abort
from flask_login import login_user, logout_user, current_user, login_required
from flask_flashy import flash
from project.models import User, Profile, Group, UserGroup, OAuthAccount
from project.utils import log, db_add
from project.access_control import generate_token, confirm_token, confirmed_check_decorator, not_confirmed_check_decorator, not_authenticated_check_decorator, validate_turnstyle, login_redirect, register_redirect
from datetime import datetime, timezone
from project.services import setup_user

@bp.route('/auth/<provider>')
def login_oauth(provider):
  connect = request.args.get("connect")
  disconnect = request.args.get("disconnect")
  if connect and current_user.is_authenticated:
    session["oauth_type"] = "connect"
  elif disconnect and current_user.is_authenticated:
    print('yes')
    for account in current_user.oauth_accounts:
      if account.provider == provider:
        print('yes')
        db.session.delete(account)
        db.session.commit()
        return redirect(url_for('views.user_settings', page='account'))
  if provider == "google":
    redirect_url = url_for('views.google_callback', _external=True)
    return oauth.google.authorize_redirect(redirect_url)
  else:
    abort(404)

@bp.route('/auth/google/callback')
def google_callback():
  provider = "google"
  try:
    token = oauth.google.authorize_access_token()
  except:
    abort(400)
  
  oauth_type = session.pop("oauth_type", None)
  if not oauth_type:
    log(request=request, description=f"oauth_type not found in session during {provider} OAuth")
    abort(400)
    
  userinfo = token['userinfo']
  oauth_account = OAuthAccount.query.filter_by(provider=provider, provider_user_id = userinfo['sub']).first()
  
  if oauth_type == "login":
    if oauth_account:
      user = oauth_account.user
      login_user(user)
      log(request=request, user=user, description=f'Logged in via {provider} OAuth')
      return redirect(url_for('views.index'))
    log(request=request, description='Failed login attempt, no oauth account found')
    return login_redirect(next=False, flash_text=f"Something went wrong. If you have an account, you must first login and connect to {provider.capitalize()} in settings. If you do not have an account, please register a new account.")
    
  elif oauth_type == "register":
    if oauth_account:
      user = oauth_account.user
      login_user(user)
      log(request=request, user=user, description=f'Logged in via {provider} OAuth via register page')
      flash('You already have an account! Logged in.')
      return redirect(url_for('views.index'))
    user = User.query.filter_by(email = userinfo['email']).first()
    if user:
      log(request=request, description='Failed register attempt, account already exists')
      return login_redirect(next=False, flash_text=f"Something went wrong. If you have an account, you must first login and connect to {provider.capitalize()} in settings. If you do not have an account, please register a new account.")
    username = session.pop("temp_username", None)
    if not username:
      log(request=request, user=user, description=f"temp_username not found in session during {provider} OAuth")
      abort(400)
    if userinfo['email_verified']:
      user = User(email=userinfo['email'], confirmed=True, date_confirmed=datetime.now(timezone.utc), tos=True, marketing=session.pop("marketing", False))
    else:
      user = User(email=userinfo['email'], unconfirmed_email=userinfo['email'], tos=True, marketing=session.pop("marketing", False))
    db_add(user)
    setup_user(user,username)
    oauth_account = OAuthAccount(
      user = user,
      provider = provider,
      provider_user_id = userinfo['sub']
    )
    db_add(oauth_account)
    log(request=request, user=user, description=f"Registered via {provider} OAuth")
    
  elif oauth_type == "connect":
    if oauth_account or current_user.is_anonymous:
      log(request=request, description='Connect attempt failed, user not logged in')
      return login_redirect(next=False, flash_text=f"Something went wrong. If you have an account, you must first login and connect to {provider.capitalize()} in settings. If you do not have an account, please register a new account.")
    oauth_account = OAuthAccount(
      user = current_user,
      provider = provider,
      provider_user_id = userinfo['sub']
    )
    db_add(oauth_account)
    log(request=request, user=current_user, description=f"Connected to {provider} OAuth")
    return redirect(url_for('views.user_settings', page="account"))
    
  return redirect(url_for('views.index'))