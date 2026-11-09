from flask import render_template, redirect, url_for, request, abort
from flask_login import current_user, login_required
from flask_flashy import flash

from project import db
from project.views import bp
from project.access_control import confirm_token, confirm_redirect, default_redirect
from project.utils import log, db_add, get_profile, get_user, get_user_profile
from project.forms import EmailChangeForm
from project.models import UserProfile
from project.services import send_email_changed_email

@bp.route('/settings/', methods=['GET', 'POST'])
@login_required
def user_settings():
  email_form = EmailChangeForm()
  if email_form.validate_on_submit():
    user = get_user(email_form.email.data, False)
    if current_user.email == email_form.email.data:
      flash('Something went wrong with your request, please try again.', 'warning')
      log(user=current_user, request=request, description='Failed email change attempt, is the same email as current')
    elif user:
      flash('Something went wrong with your request, please try again.', 'warning')
      log(user=current_user, request=request, description='Failed email change attempt, email already exists on another account')
    elif current_user.hashed_pass:
      if current_user.check_password(email_form.password.data):
        send_email_changed_email(current_user.email)
        current_user.unconfirmed_email = email_form.email.data
        current_user.confirmed = False
        current_user.date_confirmed = None
        db.session.commit()
        log(user=current_user, request=request, description='Saved new email, needs re-confirmation')
        return confirm_redirect()
      else:
        flash('Something went wrong with your request, please try again.', 'warning')
        log(user=current_user, request=request, description='Failed email change attempt, wrong password')
    else:
      flash('Something went wrong with your request, please try again.', 'warning')
      log(user=current_user, request=request, description='Failed email change attempt, no local password found')
      
  email_form = EmailChangeForm()
  return render_template('user/settings.html', email_form=email_form, subscription=current_user.stripe)

@bp.route('/settings/p/<profile>/invite/<token>')
@login_required
def profile_invite(profile:str, token:str):
  email = confirm_token(token, expiration=604800)
  if not email:
    flash("The confirmation link is invalid or has expired.", "warning")
    log(request=request, user=current_user, description=f'Profile {profile} invite confirmation failed')
    return default_redirect()
  user = get_user(email, False)
  if current_user != user:
    abort(403)
  profile = get_profile(profile)
  if user not in profile.users:
    userprofile = UserProfile(user=user, profile=profile)
    db_add(userprofile)
    log(request=request, user=current_user, description=f'Profile {profile} invite confirmation succeeded')
    flash(f"Successfully joined {profile}.", "success")
    return redirect(url_for("views.user_settings", _anchor=profile.username))
  flash("The confirmation link is invalid or has expired.", "warning")
  log(request=request, user=current_user, description=f'Profile {profile} invite confirmation failed')
  return default_redirect()
  
@bp.route('/settings/p/<profile>/owner_invite/<token>')
@login_required
def profile_owner_invite(profile:str, token:str):
  email = confirm_token(token, expiration=604800)
  if not email:
    flash("The confirmation link is invalid or has expired.", "warning")
    log(request=request, user=current_user, description=f'Profile {profile} ownership invite confirmation failed')
    return default_redirect()
  user = get_user(email, False)
  if current_user != user:
    abort(403)
  profile = get_profile(profile)
  userprofile = get_user_profile(user, profile, False)
  if not userprofile.owner:
    userprofile.owner = True
    db.session.commit()
    log(request=request, user=current_user, description=f'Profile {profile} ownership invite confirmation succeeded')
    flash(f"Successfully became owner of {profile}.", "success")
    return redirect(url_for("views.user_settings", _anchor=profile.username))
  flash("The confirmation link is invalid or has expired.", "info")
  log(request=request, user=current_user, description=f'Profile {profile} ownership invite confirmation failed')
  return default_redirect()
