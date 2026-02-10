from project.models import User
from project.utils import send_email
from project.access_control import generate_token
from flask import url_for, render_template

def send_password_reset_email(email):
  user = User.query.filter_by(email=email).first()
  if user:
    token = generate_token(email)
    confirm_url = url_for("views.password_reset_token", token=token, _external=True)
    html = render_template("email/password_reset.html", confirm_url=confirm_url, unsubscribe=False)
    subject = "Change Your vfolio Password"
    send_email([user.email],subject,html)
  return True

def send_group_invite_request_email(email,group):
  user = User.query.filter_by(email=email).first()
  if user:
    token = generate_token(email)
    confirm_url = url_for("views.group_invite", token=token, group=group, _external=True)
    html = render_template("email/group/invite_request.html", group=group, confirm_url=confirm_url, unsubscribe=False)
    subject = "vfolio Group Invite"
    send_email([user.email],subject,html)
  return True
  
def send_group_owner_request_email(email,group):
  user = User.query.filter_by(email=email).first()
  if user:
    token = generate_token(email)
    confirm_url = url_for("views.group_owner_invite", token=token, group=group, _external=True)
    html = render_template("email/group/owner_request.html", group=group, confirm_url=confirm_url, unsubscribe=False)
    subject = "vfolio Group Owner Invite"
    send_email([user.email],subject,html)
  return True
