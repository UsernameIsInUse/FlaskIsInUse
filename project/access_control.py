from flask import abort, redirect, request, url_for, current_app
from flask_login import current_user
from flask_flashy import flash
from project import authorize
from project.utils import get_group
from functools import wraps
from itsdangerous import URLSafeTimedSerializer
from requests import post, RequestException
from project.utils import log

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

def login_redirect(next=True, flash_text="You must be logged in to access this page.", color="warning"):
  flash(flash_text, color)
  if next:
    return redirect(url_for('views.login', next=request.full_path))
  else:
    return redirect(url_for('views.login'))

def register_redirect(next=True, flash_text="You must be logged in to access this page.", color="warning"):
  flash(flash_text, color)
  if next:
    return redirect(url_for('views.register', next=request.full_path))
  else:
    return redirect(url_for('views.register'))

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

def validate_turnstyle(token, secret, remoteip=None):
  url = 'https://challenges.cloudflare.com/turnstile/v0/siteverify'
  data = {
    'secret': secret,
    'response': token
  }
  if remoteip:
    data['remoteip'] = remoteip
  
  try:
    response = post(url, data=data, timeout=10)
    response.raise_for_status()
    return response.json()
  
  except RequestException as e:
    log(description='Turnstile validation error: {e}')
    return {'success':False, 'error-codes':['internal-error']}