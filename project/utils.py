from project import db
from flask_login import current_user
from flask import redirect, url_for, request, abort
import json
from flask_flashy import flash
from functools import wraps

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

def is_admin(user=current_user):
  return user.is_authenticated and user.profile.is_admin

def login_redirect(next=True):
  flash("You must be logged in to access this page.", "warning")
  return redirect(url_for('views.login', next=request.url))

def get_profile(username:str):
  """Returns a profile from a username.

  Args:
      username (str): Username of the profile.

  Returns:
      Profile
  """
  from project.models import Profile
  return Profile.query.filter_by(username=username).first_or_404()

def admin_check_decorator(f):
  @wraps(f)
  def decorated_function(*args, **kwargs):
    """Checks to see if the current_user has admin privileges."""
    if current_user.is_authenticated:
      if not current_user.profile.is_admin:
        return abort(403)
    else:
      return login_redirect()
    return f(*args, **kwargs)
  return decorated_function

def user_check_decorator(f):
  @wraps(f)
  def decorated_function(*args, **kwargs):
    """Checks to see if the current_user is the same user that is attached to the profile in the keyword arguments.
    """
    if current_user.is_authenticated:
      username = kwargs.get('username')
      profile = get_profile(username)
      if current_user.profile != profile:
        return abort(403)
    else:
      return login_redirect()
    return f(*args, **kwargs)
  return decorated_function

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
  from project.models import User, Profile, Role, ProfileRole
  profile = Profile(username="Alex")
  db_add(profile)
  user = User(email="alexcchichester@gmail.com", profile=profile)
  user.set_password("alexalex")
  db_add(user)
  role = Role(name="Admin")
  db_add(role)
  role_link = ProfileRole(profile=profile, role=role)
  db_add(role_link)