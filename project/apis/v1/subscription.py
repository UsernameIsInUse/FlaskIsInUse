
from flask import url_for, request
from flask_smorest import Blueprint
from flask.views import MethodView
from flask_login import current_user

from project.utils import log
from project.stripe import stripe, stripe_keys

from typing import List

bp = Blueprint(
    "subscriptions_v1",
    __name__,
    url_prefix="/api/v1/subscriptions"
)

def create_checkout_session(line_items:List):
  stripe.api_key = stripe_keys["secret_key"]
  customer = None
  if current_user.stripe:
    customer = current_user.stripe.stripe_customer_id
  try:
    checkout_session = stripe.checkout.Session.create(
      client_reference_id=current_user.id,
      customer=customer,
      success_url = url_for('views.subscription_success', _external=True) + "?session_id={CHECKOUT_SESSION_ID}",
      cancel_url = url_for('views.subscription_cancel', _external=True),
      mode="subscription",
      line_items=line_items
    )
    return {"sessionId": checkout_session["id"]}, 200
  except Exception as e:
    return {'error':str(e)}, 400

@bp.route("/config")
class SubscriptionConfig(MethodView):
  @bp.response(200)
  def get(self):
    if current_user.is_authenticated:
      return {'status':200, "publicKey": stripe_keys["publishable_key"]}, 200
    return {'status':401}, 401
  
@bp.route('/create-checkout-session/monthly')
class CheckoutSessionMonthly(MethodView):
  @bp.response(200)
  def get(self):
    if current_user.is_authenticated:
      log(user=current_user, request=request, description='Created stripe checkout session')
      return create_checkout_session([
        {
          "price": stripe_keys["monthly_price"],
          "quantity": 1,
        }
      ])
    return {'status':401}, 401

@bp.route('/create-checkout-session/yearly')
class CheckoutSessionYearly(MethodView):
  @bp.response(200)
  def get(self):
    if current_user.is_authenticated:
      log(user=current_user, request=request, description='Created stripe checkout session')
      return create_checkout_session(line_items=[
        {
          "price": stripe_keys["yearly_price"],
          "quantity": 1,
        }
      ])
    return {'status':401}, 401

@bp.route('/create-portal-session')
class SubscriptionPortalSession(MethodView):
  @bp.response(200)
  def get(self):
    if current_user.is_authenticated:
      if current_user.stripe:
        stripe.api_key = stripe_keys["secret_key"]
        try:
          portal_session = stripe.billing_portal.Session.create(
            customer = current_user.stripe.stripe_customer_id,
            return_url = url_for('views.user_settings', _external=True)
          )
          log(user=current_user, request=request, description='Created a stripe billing portal session')
          return {'url': portal_session.url}
        except Exception as e:
          return {'error': str(e)}, 400
      return {'status':400}, 400
    return {'status':401}, 401