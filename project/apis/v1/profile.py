from flask import request
from flask_smorest import Blueprint
from flask.views import MethodView
from flask_login import current_user

from project import db
from project.models import User, Group, UserGroup
from project.services import send_group_invite_request_email, send_group_owner_request_email

bp = Blueprint(
    "profiles_v1",
    __name__,
    url_prefix="/api/v1/profiles"
)

@bp.route("/group/remove")
class ProfileGroupRemove(MethodView):
  @bp.response(204)
  def post(self):
    data = request.form.to_dict()
    if current_user.is_authenticated:
      group = Group.query.filter_by(name=data['group']).first()
      if current_user == group.owner:
        user = User.query.filter_by(email=data['user']).first()
        if group in user.groups:
          if user != group.owner:
            usergroup = UserGroup.query.filter_by(user=user, group=group).first()
            db.session.delete(usergroup)
            db.session.commit()
            return {'status':204}, 204
          else:
            return {'status':405}, 405
        else:
          return {'status':400}, 400
      else:
        return {'status':403}, 403
    return {'status':401}, 401

@bp.route("/group/add")
class ProfileGroupAdd(MethodView):
  @bp.response(204)
  def post(self):
    data = request.form.to_dict()
    if current_user.is_authenticated:
      group = Group.query.filter_by(name=data['group']).first()
      if current_user == group.owner:
        user = User.query.filter_by(email=data['email']).first()
        if group not in user.groups:
          send_group_invite_request_email(user.email, group)
          return {'status':204}, 204
        else:
          return {'status':400}, 400
      else:
        return {'status':403}, 403
    return {'status':401}, 401

@bp.route("/group/owner")
class ProfileGroupOwner(MethodView):
  @bp.response(204)
  def post(self):
    data = request.form.to_dict()
    if current_user.is_authenticated:
      group = Group.query.filter_by(name=data['group']).first()
      if current_user == group.owner:
        user = User.query.filter_by(email=data['user']).first()
        if group in user.groups:
          if user != group.owner:
            send_group_owner_request_email(user.email, group)
            return {'status':204}, 204
          else:
            return {'status':405}, 405
        else:
          return {'status':400}, 400
      else:
        return {'status':403}, 403
    return {'status':401}, 401
    
@bp.route("/marketing")
class UserMarketingSwitch(MethodView):
  @bp.response(204)
  def patch(self):
    if current_user.is_authenticated:
      current_user.marketing = not current_user.marketing
      db.session.commit()
      return {'status':204}, 204
    return {'status':401}, 401