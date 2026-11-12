from flask import current_app
from flask_login import current_user
from flask_mail import Message

from project import db, mail
from project.common.censor import check_censor
from project.forms import UsernameForm

import json
from os import environ
from datetime import datetime, timezone
from sqlalchemy import and_

from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
  from flask import Request
  from project.models import User, Profile, UserProfile, Role, UserRole

def db_add(object) -> bool:
  """Adds the given object to the database and commits.

  Returns:
      bool: True if added.
  """
  try:
    db.session.add(object)
    db.session.commit()
    return True
  except Exception as e:
    log(data={object},description="Failed to add object to database.")
    return False

def db_delete(object) -> bool:
  """Deletes the given object from the database and commits.

  Returns:
      bool: True if removed.
  """
  try:
    db.session.delete(object)
    db.session.commit()
    return True
  except Exception as e:
    log(data={object},description="Failed to delete object from database.")
    return False

def log(data:Optional[dict]=None, request:Optional["Request"]=None, user:Optional["User"]=None, description:str=None) -> bool:
  """Creates a log using the provided arguments.

  Args:
      data (Optional[dict], optional): Data to include in the log. Defaults to None.
      request (Optional[&quot;Request&quot;], optional): Request to include in the log. Defaults to None.
      user (Optional[&quot;User&quot;], optional): User to include in the log. Defaults to None.
      description (str, optional): Description of the log. Defaults to None.

  Returns:
      bool: Whether or not creating the log was successful.
  """
  from project.models import Log
  try:
    user = user or current_user
    description = description or "Did Unspecified Action"
    try:
      if user.is_authenticated:
        d = f"{user} {description}"
      elif not user.is_anonymous:
        d = f"{user} {description}"
      else:
        d = f"Anonymous User {description}"
        user = None
    except:
      d = f"Anonymous User {description}"
      user = None
    if request:
      r = {
        "full_path": request.full_path,
        "endpoint": request.endpoint,
        "method": request.method,
        "values": request.values
      }
    else:
      r = {}
    if data:
      r.update(data)
    log = Log(user=user, data=json.dumps(r), description=d)
    db_add(log)
    return True
  except Exception as e:
    #print(e)
    return False

def get_profile(username:str, not_found:bool=True) -> "Profile":
  """Returns a profile from a username.

  Args:
      username (str): Username of the profile.
      not_found (bool): Whether or not to 404 if not found (defaults to True).

  Returns:
      Profile
  """
  from project.models import Profile
  if not_found:
    return db.first_or_404(
      db.select(Profile).where(Profile.username == username)
    )
  return db.session.scalar(
    db.select(Profile).where(Profile.username == username)
  )

def get_user(email:str, not_found:bool=True, unconfirmed:bool=False) -> "User":
  """Returns a user from an email.

  Args:
      email (str): Email of the user.
      not_found (bool): Whether or not to 404 if not found (defaults to True).
      not_found (bool): Whether or not to search unconfirmed email (defaults to False).

  Returns:
      User
  """
  from project.models import User
  if unconfirmed:
    if not_found:
      return db.first_or_404(
        db.select(User).where(User.unconfirmed_email == email)
      )
    return db.session.scalar(
      db.select(User).where(User.unconfirmed_email == email)
    )
  if not_found:
    return db.first_or_404(
      db.select(User).where(User.email == email)
    )
  return db.session.scalar(
    db.select(User).where(User.email == email)
  )

def get_user_profile(user:User, profile:Profile, not_found:bool=True) -> "UserProfile":
  """Returns a userprofile from a user and a profile.

  Args:
      user (User): User object.
      profile (Profile): Profile object.
      not_found (bool): Whether or not to 404 if not found (defaults to True).

  Returns:
      UserProfile
  """
  from project.models import UserProfile
  if not_found:
    return db.first_or_404(
      db.select(UserProfile).where(and_(UserProfile.user == user, UserProfile.profile == profile))
    )
  return db.session.scalar(
    db.select(UserProfile).where(and_(UserProfile.user == user, UserProfile.profile == profile))
  )

def get_role(name:str, not_found:bool=True) -> "Role":
  """Returns a role from a name.

  Args:
      name (str): Name of the role.
      not_found (bool): Whether or not to 404 if not found (defaults to True).

  Returns:
      Role
  """
  from project.models import Role
  if not_found:
    return db.first_or_404(
      db.select(Role).where(Role.name == name)
    )
  return db.session.scalar(
    db.select(Role).where(Role.name == name)
  )

def get_user_role(user:User, role:Role, not_found:bool=True) -> "UserRole":
  """Returns a userrole from a user and a role.

  Args:
      user (User): User object.
      role (Role): Role object.
      not_found (bool): Whether or not to 404 if not found (defaults to True).

  Returns:
      UserProfile
  """
  from project.models import UserRole
  if not_found:
    return db.first_or_404(
      db.select(UserRole).where(and_(UserRole.user == user, UserRole.role == role))
    )
  return db.session.scalar(
    db.select(UserRole).where(and_(UserRole.user == user, UserRole.role == role))
  )

def reset_database(dev=False) -> bool:
  """Resets the database.

  Returns:
      bool: True if reset.
  """
  import project.models
  try:
    db.drop_all()
    db.create_all()
    if dev:
      dev_database()
    return True
  except Exception as e:
    #print(e)
    return False
  
def dev_database():
  """Creates an Admin user from environment variables."""
  from project.models import User, Role, UserRole, Profile, UserProfile
  user = User(email=environ['DEV_EMAIL'], confirmed=True, date_confirmed=datetime.now(timezone.utc))
  user.set_password(environ['DEV_PASS'])
  db_add(user)
  profile = Profile(username=environ["DEV_USER"])
  db_add(profile)
  userprofile = UserProfile(user=user, profile=profile, owner=True)
  db_add(userprofile)
  admin = Role(name="Admin")
  db_add(admin)
  userrole = UserRole(user=user, role=admin)
  db_add(userrole)
  
def send_email(recipients:list,subject:str,html:str) -> bool:
  """Sends individual emails to a list of recipients.

  Args:
      recipients (list): List of recipients to individually be emailed.
      subject (str): Subject of the email.
      html (str): Body of the email.
  """
  try:
    for recipient in recipients:
      msg = Message(
        subject=subject,
        recipients=[recipient],
        html=html,
        sender=current_app.config["MAIL_DEFAULT_SENDER"]
      )
      mail.send(msg)
      log(f'Email Sent: {subject} to {recipient}')
      return True
  except:
    log(f'Email Failed to Send: {subject} to {recipient}')
    return False

def check_username(username:str) -> bool:
  """Checks a given username against blocklist, censor, and list of current usernames to determine whether or not it is available for use.

  Args:
      username (str): Username to check.

  Returns:
      bool: True if available.
  """
  if not UsernameForm(data={'username': username}).validate() or get_profile(username, False) or check_censor(username):
    return False
  return True