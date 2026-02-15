from project.models import User, Group, Profile, UserGroup
from project.utils import send_email, db_add, log
from project.access_control import generate_token
from flask import url_for, render_template

def send_email_confirmation_email(email):
  user = User.query.filter_by(unconfirmed_email=email).first()
  if user:
    token = generate_token(email)
    confirm_url = url_for("views.confirm_email", token=token, _external=True)
    html = render_template("email/email_confirmation.html", confirm_url=confirm_url, unsubscribe=False)
    subject = "Confirm Your vfolio Account"
    send_email([email],subject,html)
  return True

def send_password_reset_email(email):
  user = User.query.filter_by(email=email).first()
  if user:
    token = generate_token(email)
    confirm_url = url_for("views.password_reset_token", token=token, _external=True)
    html = render_template("email/password_reset.html", confirm_url=confirm_url, unsubscribe=False)
    subject = "Change Your vfolio Password"
    send_email([email],subject,html)
  return True

def send_group_invite_request_email(email,group):
  user = User.query.filter_by(email=email).first()
  if user:
    token = generate_token(email)
    confirm_url = url_for("views.group_invite", token=token, group=group, _external=True)
    html = render_template("email/group/invite_request.html", group=group, confirm_url=confirm_url, unsubscribe=False)
    subject = "vfolio Group Invite"
    send_email([email],subject,html)
  return True
  
def send_group_owner_request_email(email,group):
  user = User.query.filter_by(email=email).first()
  if user:
    token = generate_token(email)
    confirm_url = url_for("views.group_owner_invite", token=token, group=group, _external=True)
    html = render_template("email/group/owner_request.html", group=group, confirm_url=confirm_url, unsubscribe=False)
    subject = "vfolio Group Owner Invite"
    send_email([email],subject,html)
  return True  

def send_email_changed_email(email):
  user = User.query.filter_by(email=email).first()
  if user:
    html = render_template("email/email_change.html", unsubscribe=False)
    subject = "Your vfolio Email Has Been Changed"
    send_email([email],subject,html)
  return True

def setup_user(user,username):
  group = Group(name=username)
  db_add(group)
  profile = Profile(username=username, group=group, owner=user)
  db_add(profile)
  usergroup = UserGroup(user=user, group=group)
  db_add(usergroup)
  log(user=user, description='User setup')
  