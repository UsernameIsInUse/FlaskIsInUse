from flask import render_template
from flask_login import current_user

from project.views import bp
from project.access_control import user_check_decorator, login_redirect

@bp.route('/profile/<username>')
@user_check_decorator
def profile(username:str):
  if current_user.is_anonymous:
    return login_redirect()
  return render_template('profile/profile.html')