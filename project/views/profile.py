from flask import render_template

from project.views import bp
from project.models.profile import Profile
from project.utils import get_profile

@bp.route('/profile/<username>')
def profile(username:str):
  profile = get_profile(username)
  return render_template('profile/profile.html', profile=profile)