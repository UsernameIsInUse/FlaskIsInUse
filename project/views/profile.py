from flask import render_template, redirect, url_for, request
from flask_login import current_user
from project.views import bp
from project.utils import user_check_decorator

@bp.route('/profile/<username>')
@user_check_decorator
def profile(username):
  if current_user.is_anonymous:
    return redirect(url_for('views.login', next=request.full_path))
  return render_template('profile/profile.html')