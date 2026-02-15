from project import db, mail
from flask_login import current_user
import json
from os import environ
from flask_mail import Message
from flask import current_app

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
    print(e)
    return False

def log(data:dict=None, request=None, user=None, description:str=None) -> bool:
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
    print(e)
    return False

def get_profile(username:str):
  """Returns a profile from a username.

  Args:
      username (str): Username of the profile.

  Returns:
      Profile
  """
  from project.models import Profile
  return Profile.query.filter_by(username=username).first_or_404()

def get_group(username:str):
  """Returns a group from a username.

  Args:
      username (str): Username of the profile.

  Returns:
      Profile
  """
  from project.models import Group
  return Group.query.filter_by(name=username).first_or_404()

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
    print(e)
    return False
  
def dev_database() -> bool:
  from project.models import User, Profile, Group, UserGroup, Role, UserRole
  user = User(email=environ['DEV_EMAIL'], confirmed=True)
  user.set_password(environ['DEV_PASS'])
  db_add(user)
  group = Group(name=environ["DEV_USER"])
  db_add(group)
  profile = Profile(username=environ["DEV_USER"], group=group, owner=user)
  db_add(profile)
  usergroup = UserGroup(user=user, group=group)
  db_add(usergroup)
  admin = Role(name="Admin")
  db_add(admin)
  userrole = UserRole(user=user, role=admin)
  db_add(userrole)
  
def send_email(recipients:list,subject:str,html:str):
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
  except:
    log(f'Email Failed to Send: {subject} to {recipient}')
