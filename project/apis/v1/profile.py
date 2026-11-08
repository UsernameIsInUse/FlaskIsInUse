from flask import request
from flask_smorest import Blueprint
from flask.views import MethodView
from flask_login import current_user

from project import db
from project.models import User, Profile, UserProfile
from project.services import send_profile_invite_request_email, send_profile_owner_request_email
from project.utils import log
from project.access_control import is_owner, is_member

bp = Blueprint(
    "profiles_v1",
    __name__,
    url_prefix="/api/v1/profiles"
)

@bp.route("/user/add")
class ProfileUserAdd(MethodView):
  @bp.response(200)
  def post(self):
    data = request.get_json()
    profile = Profile.query.filter_by(username=data['profile']).first()
    user = User.query.filter_by(email=data['email']).first()
    
    if not current_user.is_authenticated:
      log(request=request, description='Failed to add user to profile, current user not logged in')
      return {'status':401, 'message':'You must be logged in to perform this action.'}, 401
    elif not is_owner(profile):
      log(request=request, description='Failed to add user to profile, current user not profile owner')
      return {'status':403, 'message':'Only a profile owner can add users to profiles.'}, 403
    elif not user:
      if send_profile_invite_request_email(data['email'], profile):
        return {'status':200, 'message':'Invite request sent.'}, 200
      return {'status':500, 'message':'Something went wrong.'}, 500
    elif profile in user.profiles:
      log(request=request, description='Failed to add user to profile, user already in profile')
      return {'status':400, 'message':'User already in profile.'}, 400
    if send_profile_invite_request_email(data['email'], profile):
      return {'status':200, 'message':'Invite request sent.'}, 200
    return {'status':500, 'message':'Something went wrong.'}, 500

@bp.route("/user/remove")
class ProfileUserRemove(MethodView):
  @bp.response(200)
  def post(self):
    data = request.get_json()
    profile = Profile.query.filter_by(username=data['profile']).first()
    user = User.query.filter_by(email=data['email']).first()
    
    if not current_user.is_authenticated:
      log(request=request, description='Failed to remove user from profile, current user not logged in')
      return {'status':401, 'message':'You must be logged in to perform this action.'}, 401
    elif not is_owner(profile):
      log(request=request, description='Failed to remove user from profile, current user not profile owner')
      return {'status':403, 'message':'Only a profile owner can remove users from profiles.'}, 403
    elif not user:
      log(request=request, description='Failed to remove user from profile, user does not exist')
      return {'status':400, 'message':'User already not in profile.'}, 400
    elif profile not in user.profiles:
      log(request=request, description='Failed to remove user from profile, user not in profile')
      return {'status':400, 'message':'User already not in profile.'}, 400
    elif user == current_user:
      log(request=request, description='Failed to remove user from profile, user is current user')
      return {'status':403, 'message':'Cannot remove yourself from profile.'}, 403
    userprofile = UserProfile.query.filter_by(user=user, profile=profile).first()
    db.session.delete(userprofile)
    db.session.commit()
    return {'status':200, 'message':'User removed from profile.'}, 200

@bp.route("/user/owner/add")
class ProfileUserOwnerAdd(MethodView):
  @bp.response(200)
  def post(self):
    data = request.get_json()
    profile = Profile.query.filter_by(username=data['profile']).first()
    user = User.query.filter_by(email=data['email']).first()
    
    if not current_user.is_authenticated:
      log(request=request, description='Failed to add profile owner, current user not logged in')
      return {'status':401, 'message':'You must be logged in to perform this action.'}, 401
    elif not is_owner(profile):
      log(request=request, description='Failed to add profile owner, current user not profile owner')
      return {'status':403, 'message':'Only a profile owner can add additional owners.'}, 403
    elif not user:
      log(request=request, description='Failed to add profile owner, user does not exist')
      return {'status':400, 'message':'User must be a member of the profile before ownership can be added.'}, 400
    elif profile not in user.profiles:
      log(request=request, description='Failed to add profile owner, user not in profile')
      return {'status':400, 'message':'User must be a member of the profile before ownership can be added.'}, 400
    if send_profile_owner_request_email(user.email, profile):
      return {'status':200, 'message':'Ownership invite request sent.'}, 200
    return {'status':500, 'message':'Something went wrong.'}, 500
  
@bp.route("/user/owner/remove")
class ProfileUserOwnerRemove(MethodView):
  @bp.response(200)
  def post(self):
    data = request.get_json()
    profile = Profile.query.filter_by(username=data['profile']).first()
    user = User.query.filter_by(email=data['email']).first()
    
    if not current_user.is_authenticated:
      log(request=request, description='Failed to remove profile owner, current user not logged in')
      return {'status':401, 'message':'You must be logged in to perform this action.'}, 401
    elif not is_owner(profile):
      log(request=request, description='Failed to remove profile owner, current user not profile owner')
      return {'status':403, 'message':'Only a profile owner can remove other owners.'}, 403
    elif not user:
      log(request=request, description='Failed to remove profile owner, user does not exist')
      return {'status':400, 'message':'User must be a profile owner before ownership can be removed.'}, 400
    elif profile not in user.profiles:
      log(request=request, description='Failed to remove profile owner, user not in profile')
      return {'status':400, 'message':'User must be a profile owner before ownership can be removed.'}, 400
    elif user not in profile.owners:
      log(request=request, description='Failed to remove profile owner, user not an owner')
      return {'status':400, 'message':'User must be a profile owner before ownership can be removed.'}, 400
    userprofile = UserProfile.query.filter_by(user=user, profile=profile).first()
    userprofile.owner = False
    db.session.commit()
    return {'status':200, 'message':'User removed from owners.'}, 200