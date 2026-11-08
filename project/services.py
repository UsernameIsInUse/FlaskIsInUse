from flask import url_for, render_template

from project.models import User, Profile, UserProfile
from project.utils import send_email, db_add, log, get_user
from project.access_control import generate_token

def send_email_confirmation_email(email:str) -> bool:
  """Sends an email confirmation email to the provided email address.

  Args:
      email (str): The email address to send to.

  Returns:
      bool: Whether or not the email was sent successfully.
  """
  user = get_user(email,False,True)
  if user:
    token = generate_token(email)
    confirm_url = url_for("views.confirm_email", token=token, _external=True)
    html = render_template("email/email_confirmation.html", confirm_url=confirm_url, unsubscribe=False)
    subject = "Confirm Your FlaskIsInUse Account"
    return send_email([email],subject,html)
  return False

def send_password_reset_email(email:str) -> bool:
  """Sends a password reeset email to the provided email address.

  Args:
      email (str): The email address to send to.

  Returns:
      bool: Whether or not the email was sent successfully.
  """
  user = get_user(email,False)
  if user:
    token = generate_token(email)
    confirm_url = url_for("views.password_reset_token", token=token, _external=True)
    html = render_template("email/password_reset.html", confirm_url=confirm_url, unsubscribe=False)
    subject = "Change Your FlaskIsInUse Password"
    return send_email([email],subject,html)
  return False

def send_profile_invite_request_email(email:str, profile:Profile) -> bool:
  """Sends a profile invite email to the provided email address.

  Args:
      email (str): The email address to send to.
      profile (Profile): The Profile the email is being invited to.

  Returns:
      bool: Whether or not the email was sent successfully.
  """
  token = generate_token(email)
  confirm_url = url_for("views.profile_invite", token=token, profile=profile, _external=True)
  html = render_template("email/profile/invite_request.html", profile=profile, confirm_url=confirm_url, unsubscribe=False)
  subject = "FlaskIsInUse Profile Invite"
  return send_email([email],subject,html)
  
def send_profile_owner_request_email(email:str, profile:Profile) -> bool:
  """Sends a profile ownership request email to the provided email address.

  Args:
      email (str): The email address to send to.
      profile (Profile): The Profile the email is being invited to own.

  Returns:
      bool: Whether or not the email was sent successfully.
  """
  user = get_user(email,False)
  if user:
    token = generate_token(email)
    confirm_url = url_for("views.profile_owner_invite", token=token, profile=profile, _external=True)
    html = render_template("email/profile/owner_request.html", profile=profile, confirm_url=confirm_url, unsubscribe=False)
    subject = "FlaskIsInUse Profile Owner Invite"
    return send_email([email],subject,html)
  return False

def send_email_changed_email(email:str) -> bool:
  """Sends an email changed notification email to the provided email address.

  Args:
      email (str): The email address to send to.

  Returns:
      bool: Whether or not the email was sent successfully.
  """
  user = get_user(email,False)
  if user:
    html = render_template("email/email_change.html", unsubscribe=False)
    subject = "Your FlaskIsInUse Email Has Been Changed"
    return send_email([email],subject,html)
  return False

def setup_user(user:User,username:str):
  """Creates a Profile and UserProfile connected to the User with a given Username.

  Args:
      user (User): The User to setup.
      username (str): The username to use for the Profile.
  """
  profile = Profile(username=username)
  db_add(profile)
  userprofile = UserProfile(user=user, profile=profile, owner=True)
  db_add(userprofile)
  log(user=user, description='User setup')
  