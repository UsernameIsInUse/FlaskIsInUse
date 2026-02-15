from flask import render_template, redirect, url_for, request
from flask_login import current_user, fresh_login_required, login_required
from project.views import bp
from project.access_control import confirm_token
from project.utils import send_email, log
from project.forms import EmailChangeForm
from project.models import User, Group, UserGroup
from project.services import send_email_changed_email
from project import db
from flask_flashy import flash

@bp.route('/settings/', methods=['GET', 'POST'])
@login_required
def user_settings():
  email_form = EmailChangeForm()
  if email_form.validate_on_submit():
    user = User.query.filter_by(email=email_form.email.data).first()
    if current_user.email == email_form.email.data:
      flash('Something went wrong with your request, please try again.', 'warning')
      log(user=current_user, request=request, description='Failed email change attempt')
    elif user:
      flash('Something went wrong with your request, please try again.', 'warning')
      log(user=current_user, request=request, description='Failed email change attempt')
    else:
      send_email_changed_email(current_user.email)
      current_user.unconfirmed_email = email_form.email.data
      current_user.confirmed = False
      current_user.date_confirmed = None
      db.session.commit()
      log(user=current_user, request=request, description='Saved new email, needs re-confirmation')
      return redirect(url_for('views.confirm'))
  email_form = EmailChangeForm()
  return render_template('user/settings.html', email_form=email_form, subscription=current_user.stripe)

@bp.route('/settings/g/<group>/invite/<token>')
@login_required
def group_invite(group, token):
  email = confirm_token(token, expiration=604800)
  user = User.query.filter_by(email=email).first()
  group = Group.query.filter_by(name=group).first()
  if current_user == user and user not in group.users:
    ug = UserGroup(user=current_user, group=group)
    db.session.add(ug)
    db.session.commit()
    log(request=request, user=current_user, description=f'Group {group} invite confirmation succeeded')
    flash(f"Successfully joined {group}.", "success")
    return redirect(url_for("views.user_settings"))
  flash("The confirmation link is invalid or has expired.", "info")
  log(request=request, user=current_user, description=f'Group {group} invite confirmation failed')
  return redirect(url_for("views.user_settings"))
  
@bp.route('/settings/g/<group>/owner_invite/<token>')
@login_required
def group_owner_invite(group, token):
  email = confirm_token(token, expiration=604800)
  user = User.query.filter_by(email=email).first()
  group = Group.query.filter_by(name=group).first()
  if current_user == user and user != group.owner:
    group.profile.owner = current_user
    db.session.commit()
    log(request=request, user=current_user, description=f'Group {group} ownership invite confirmation succeeded')
    flash(f"Successfully became owner of {group}.", "success")
    return redirect(url_for("views.user_settings"))
  flash("The confirmation link is invalid or has expired.", "info")
  log(request=request, user=current_user, description=f'Group {group} ownership invite confirmation failed')
  return redirect(url_for("views.user_settings"))
