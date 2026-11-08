from flask import render_template

from project.views import bp
from project.models.profile import Profile

@bp.route('/profile/<username>')
def profile(username:str):
  profile = Profile.query.filter_by(username=username).first()
  return render_template('profile/profile.html', profile=profile)