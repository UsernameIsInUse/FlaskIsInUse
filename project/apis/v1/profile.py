from flask import request
from flask_smorest import Blueprint
from flask.views import MethodView
from flask_login import current_user

from project import db
from project.models import User, Group, UserGroup
from project.services import send_group_invite_request_email, send_group_owner_request_email
from project.utils import log

bp = Blueprint(
    "profiles_v1",
    __name__,
    url_prefix="/api/v1/profiles"
)

@bp.route("/group/remove")
class ProfileGroupRemove(MethodView):
  @bp.response(200)
  def post(self):
    data = request.get_json()
    group = Group.query.filter_by(name=data['group']).first()
    user = User.query.filter_by(email=data['email']).first()
    
    if not current_user.is_authenticated:
      log(request=request, description='Failed to remove user from group, current user not logged in')
      return {'status':401, 'message':'You must be logged in to perform this action.'}, 401
    elif current_user != group.owner:
      log(request=request, description='Failed to remove user from group, current user not group owner')
      return {'status':403, 'message':'Only the group owner can remove users from groups.'}, 403
    elif not user:
      log(request=request, description='Failed to remove user from group, user does not exist')
      return {'status':400, 'message':'User already not in group.'}, 400
    elif group not in user.groups:
      log(request=request, description='Failed to remove user from group, user not in group')
      return {'status':400, 'message':'User already not in group.'}, 400
    elif user == group.owner:
      log(request=request, description='Failed to remove user from group, user is owner')
      return {'status':403, 'message':'Cannot remove owner from group.'}, 403
    usergroup = UserGroup.query.filter_by(user=user, group=group).first()
    db.session.delete(usergroup)
    db.session.commit()
    return {'status':200, 'message':'User removed from group.'}, 200

@bp.route("/group/add")
class ProfileGroupAdd(MethodView):
  @bp.response(200)
  def post(self):
    data = request.get_json()
    group = Group.query.filter_by(name=data['group']).first()
    user = User.query.filter_by(email=data['email']).first()
    
    if not current_user.is_authenticated:
      log(request=request, description='Failed to add user to group, current user not logged in')
      return {'status':401, 'message':'You must be logged in to perform this action.'}, 401
    elif current_user != group.owner:
      log(request=request, description='Failed to add user to group, current user not group owner')
      return {'status':403, 'message':'Only the group owner can add users to groups.'}, 403
    elif not user:
      if send_group_invite_request_email(data['email'], group):
        return {'status':200, 'message':'Invite request sent.'}, 200
      return {'status':500, 'message':'Something went wrong.'}, 500
    elif group in user.groups:
      log(request=request, description='Failed to add user to group, user already in group')
      return {'status':400, 'message':'User already in group.'}, 400
    if send_group_invite_request_email(data['email'], group):
      return {'status':200, 'message':'Invite request sent.'}, 200
    return {'status':500, 'message':'Something went wrong.'}, 500

@bp.route("/group/owner")
class ProfileGroupOwner(MethodView):
  @bp.response(200)
  def post(self):
    data = request.get_json()
    group = Group.query.filter_by(name=data['group']).first()
    user = User.query.filter_by(email=data['email']).first()
    
    if not current_user.is_authenticated:
      log(request=request, description='Failed to request group owner transfer, current user not logged in')
      return {'status':401, 'message':'You must be logged in to perform this action.'}, 401
    elif current_user != group.owner:
      log(request=request, description='Failed to request group owner transfer, current user not group owner')
      return {'status':403, 'message':'Only the group owner can transfer ownership.'}, 403
    elif not user:
      log(request=request, description='Failed to request group owner transfer, user does not exist')
      return {'status':400, 'message':'User must be a member of the group before ownership can be transferred.'}, 400
    elif group not in user.groups:
      log(request=request, description='Failed to request group owner transfer, user not in group')
      return {'status':400, 'message':'User must be a member of the group before ownership can be transferred.'}, 400
    if send_group_owner_request_email(user.email, group):
      return {'status':200, 'message':'Ownership transfer request sent.'}, 200
    return {'status':500, 'message':'Something went wrong.'}, 500