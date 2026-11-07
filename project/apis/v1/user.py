from flask import request
from flask_smorest import Blueprint
from flask.views import MethodView
from flask_login import current_user

from project.services import send_password_reset_email, send_email_confirmation_email
from project import db
from project.utils import log

bp = Blueprint(
  'users_v1',
  __name__,
  url_prefix='/api/v1/users'
)

@bp.route('/reset_password')
class UserResetPassword(MethodView):
  @bp.response(202)
  def post(self):
    data = request.get_json()
    email = data.get('email')
    send_password_reset_email(email)
    return {'status':202, 'message':'If the email exists, instructions were sent to reset the password.'}, 202

@bp.route('/marketing')
class UserMarketingSwitch(MethodView):
  @bp.response(204)
  def patch(self):
    if current_user.is_authenticated:
      current_user.marketing = not current_user.marketing
      db.session.commit()
      log(request=request, description=f'Set marketing to {current_user.marketing}')
      return {'status':204, 'message':'Updated marketing preferences.'}, 204
    log(request=request, description=f'Failed to change marketing preferences')
    return {'status':401, 'message':'Failed to change marketing preferences.'}, 401
  
@bp.route('/send_confirm_email')
class UserSendEmailConfirmation(MethodView):
  @bp.response(202)
  def post(self):
    if current_user.is_authenticated:
      if not current_user.confirmed:
        send_email_confirmation_email(current_user.unconfirmed_email)
        return {'status':202, 'message':'Sent email confirmation.'}, 202
      log(request=request, description=f'Tried to send email confirmation, user already confirmed')
      return {'status':405, 'message':'Failed to send email confirmation.'}, 405
    log(request=request, description=f'Failed to send email confirmation')
    return {'status':401, 'message':'Failed to send email confirmation.'}, 401