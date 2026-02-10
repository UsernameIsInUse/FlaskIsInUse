from flask import abort, redirect, request, url_for, current_app
from flask_login import current_user
from flask_flashy import flash
from project import authorize
from project.utils import get_group
from functools import wraps
from itsdangerous import URLSafeTimedSerializer

def is_admin(user=current_user):
  return authorize.has_role('Admin')(user)

def admin_check_decorator(f):
  @wraps(f)
  def decorated_function(*args, **kwargs):
    """The user must be authenticated and an admin to proceed."""
    if current_user.is_authenticated:
      if not is_admin():
          return abort(403)
    else:
      return login_redirect()
    return f(*args, **kwargs)
  return decorated_function

def user_check_decorator(f):
  @wraps(f)
  def decorated_function(*args, **kwargs):
    """The user must be authenticated and belong to the profile group."""
    if current_user.is_authenticated:
      if not authorize.in_group(kwargs.get("username"))(current_user):
        abort(403)
    else:
      return login_redirect()
    return f(*args, **kwargs)
  return decorated_function

def confirmed_check_decorator(f):
  @wraps(f)
  def decorated_function(*args, **kwargs):
    """The user, if authenticated, must have email confirmed."""
    if current_user.is_authenticated and not current_user.confirmed:
      flash('You must confirm your email to proceed.', 'info')
      return redirect(url_for("views.confirm"))
    return f(*args, **kwargs)
  return decorated_function

def not_confirmed_check_decorator(f):
  @wraps(f)
  def decorated_function(*args, **kwargs):
    """The user, if authenticated, must not have email confirmed."""
    if current_user.is_authenticated and current_user.confirmed:
      flash('Email already confirmed.', 'info')
      return redirect(url_for('views.index'))
    return f(*args, **kwargs)
  return decorated_function

def not_authenticated_check_decorator(f):
  @wraps(f)
  def decorated_function(*args, **kwargs):
    """The user must not be authenticated to proceed."""
    if current_user.is_authenticated:
      flash('Already logged in.', 'info')
      return redirect(url_for('views.index'))
    return f(*args, **kwargs)
  return decorated_function

def login_redirect(next=True):
  flash("You must be logged in to access this page.", "warning")
  return redirect(url_for('views.login', next=request.full_path))

def generate_token(email:str) -> str:
  """Generates a secure URLSafe Timed Serializer token for emails.

  Args:
      email (str): Email address used to create the token.

  Returns:
      str: Token
  """
  serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
  return serializer.dumps(email, salt=current_app.config["SECURITY_PASSWORD_SALT"])

def confirm_token(token:str, expiration:int=3600) -> str:
  """Confirms a serializer token based on a given expiration time in seconds.

  Args:
      token (str)
      expiration (int, optional): Expiration in seconds. Defaults to 3600.

  Returns:
      str: Email address.
  """
  serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
  try:
    email = serializer.loads(
      token, salt=current_app.config["SECURITY_PASSWORD_SALT"], max_age=expiration
    )
    return email
  except Exception:
    return False
