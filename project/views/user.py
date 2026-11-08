from flask import render_template, redirect, url_for, request, abort
from flask_login import current_user, login_required
from flask_flashy import flash

from project import db
from project.views import bp
from project.access_control import confirm_token
from project.utils import log
from project.forms import EmailChangeForm
from project.models import User, Profile, UserProfile
from project.services import send_email_changed_email

@bp.route('/settings/', methods=['GET', 'POST'])
@login_required
def user_settings():
  email_form = EmailChangeForm()
  if email_form.validate_on_submit():
    user = User.query.filter_by(email=email_form.email.data).first()
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
        return redirect(url_for('views.confirm'))
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
    return redirect(url_for("views.user_settings"))
  user = User.query.filter_by(email=email).first()
  profile = Profile.query.filter_by(username=profile).first()
  if current_user != user:
    abort(403)
  if user not in profile.users:
    userprofile = UserProfile(user=user, profile=profile)
    db.session.add(userprofile)
    db.session.commit()
    log(request=request, user=current_user, description=f'Profile {profile} invite confirmation succeeded')
    flash(f"Successfully joined {profile}.", "success")
    return redirect(url_for("views.user_settings"))
  flash("The confirmation link is invalid or has expired.", "warning")
  log(request=request, user=current_user, description=f'Profile {profile} invite confirmation failed')
  return redirect(url_for("views.user_settings"))
  
@bp.route('/settings/p/<profile>/owner_invite/<token>')
@login_required
def profile_owner_invite(profile:str, token:str):
  email = confirm_token(token, expiration=604800)
  if not email:
    flash("The confirmation link is invalid or has expired.", "warning")
    log(request=request, user=current_user, description=f'Profile {profile} ownership invite confirmation failed')
    return redirect(url_for("views.user_settings"))
  user = User.query.filter_by(email=email).first()
  profile = Profile.query.filter_by(username=profile).first()
  userprofile = UserProfile.query.filter_by(user=user, profile=profile).first()
  if current_user != user:
    abort(403)
  if not userprofile.owner:
    userprofile.owner = True
    db.session.commit()
    log(request=request, user=current_user, description=f'Profile {profile} ownership invite confirmation succeeded')
    flash(f"Successfully became owner of {profile}.", "success")
    return redirect(url_for("views.user_settings"))
  flash("The confirmation link is invalid or has expired.", "info")
  log(request=request, user=current_user, description=f'Profile {profile} ownership invite confirmation failed')
  return redirect(url_for("views.user_settings"))
