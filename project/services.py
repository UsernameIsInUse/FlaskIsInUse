from flask import url_for, render_template

from project.models import User, Group, Profile, UserGroup
from project.utils import send_email, db_add, log
from project.access_control import generate_token

from typing import TYPE_CHECKING
if TYPE_CHECKING:
  from project.models import Group

def send_email_confirmation_email(email:str) -> bool:
  """Sends an email confirmation email to the provided email address.

  Args:
      email (str): The email address to send to.

  Returns:
      bool: Whether or not the email was sent successfully.
  """
  user = User.query.filter_by(unconfirmed_email=email).first()
  if user:
    token = generate_token(email)
    confirm_url = url_for("views.confirm_email", token=token, _external=True)
    html = render_template("email/email_confirmation.html", confirm_url=confirm_url, unsubscribe=False)
    subject = "Confirm Your vfolio Account"
    return send_email([email],subject,html)
  return False

def send_password_reset_email(email:str) -> bool:
  """Sends a password reeset email to the provided email address.

  Args:
      email (str): The email address to send to.

  Returns:
      bool: Whether or not the email was sent successfully.
  """
  user = User.query.filter_by(email=email).first()
  if user:
    token = generate_token(email)
    confirm_url = url_for("views.password_reset_token", token=token, _external=True)
    html = render_template("email/password_reset.html", confirm_url=confirm_url, unsubscribe=False)
    subject = "Change Your vfolio Password"
    return send_email([email],subject,html)
  return False

def send_group_invite_request_email(email:str, group:Group) -> bool:
  """Sends a group invite email to the provided email address.

  Args:
      email (str): The email address to send to.
      group (Group): The Group the email is being invited to.

  Returns:
      bool: Whether or not the email was sent successfully.
  """
  user = User.query.filter_by(email=email).first()
  if user:
    token = generate_token(email)
    confirm_url = url_for("views.group_invite", token=token, group=group, _external=True)
    html = render_template("email/group/invite_request.html", group=group, confirm_url=confirm_url, unsubscribe=False)
    subject = "vfolio Group Invite"
    return send_email([email],subject,html)
  return False
  
def send_group_owner_request_email(email:str, group:Group) -> bool:
  """Sends a group ownership request email to the provided email address.

  Args:
      email (str): The email address to send to.
      group (Group): The Group the email is being invited to own.

  Returns:
      bool: Whether or not the email was sent successfully.
  """
  user = User.query.filter_by(email=email).first()
  if user:
    token = generate_token(email)
    confirm_url = url_for("views.group_owner_invite", token=token, group=group, _external=True)
    html = render_template("email/group/owner_request.html", group=group, confirm_url=confirm_url, unsubscribe=False)
    subject = "vfolio Group Owner Invite"
    return send_email([email],subject,html)
  return False

def send_email_changed_email(email:str) -> bool:
  """Sends an email changed notification email to the provided email address.

  Args:
      email (str): The email address to send to.

  Returns:
      bool: Whether or not the email was sent successfully.
  """
  user = User.query.filter_by(email=email).first()
  if user:
    html = render_template("email/email_change.html", unsubscribe=False)
    subject = "Your vfolio Email Has Been Changed"
    return send_email([email],subject,html)
  return False

def setup_user(user:User,username:str):
  """Creates a Group, Profile, and UserGroup connected to the User with a given Username.

  Args:
      user (User): The User to setup.
      username (str): The username to use for the Group and Profile.
  """
  group = Group(name=username)
  db_add(group)
  profile = Profile(username=username, group=group, owner=user)
  db_add(profile)
  usergroup = UserGroup(user=user, group=group)
  db_add(usergroup)
  log(user=user, description='User setup')
  