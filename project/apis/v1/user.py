from flask_smorest import Blueprint
from flask.views import MethodView
from project.services import send_password_reset_email
from flask import request
from flask_login import current_user
from project import db
from project.utils import log

bp = Blueprint(
  "users_v1",
  __name__,
  url_prefix="/api/v1/users"
)

@bp.route("/reset_password")
class UserResetPassword(MethodView):
  @bp.response(202)
  def post(self):
    email = request.form.get("email")
    send_password_reset_email(email)
    return {'status':202}, 202

@bp.route("/marketing")
class UserMarketingSwitch(MethodView):
  @bp.response(204)
  def patch(self):
    if current_user.is_authenticated:
      current_user.marketing = not current_user.marketing
      db.session.commit()
      log(request=request, description=f"Set marketing to {current_user.marketing}")
      return {'status':204}, 204
    log(request=request, description=f"Failed to change marketing settings")
    return {'status':401}, 401
    