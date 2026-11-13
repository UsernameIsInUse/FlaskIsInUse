from flask import redirect, url_for, request
from flask_login import current_user, login_required

from project.views import bp
from project.utils import log, db_add
from project.stripe import stripe, stripe_keys
from project.models import User, StripeCustomer
from project.extensions import db, csrf

from uuid import UUID

@bp.route('/subscription/', methods=['POST','GET'])
@login_required
def subscription():
  return redirect(url_for('views.user_settings', _anchor="subscription"))

@bp.route('/subscription/success', methods=['POST','GET'])
@login_required
def subscription_success():
  return redirect(url_for('views.user_settings', _anchor="subscription"))

@bp.route('/subscription/cancel', methods=['POST','GET'])
@login_required
def subscription_cancel():
  return redirect(url_for('views.user_settings', _anchor="subscription"))

@bp.route("/subscription/webhook", methods=["POST"])
@csrf.exempt
def stripe_webhook():
  payload = request.get_data(cache=True, as_text=False)
  sig_header = request.headers.get("Stripe-Signature")
  endpoint_secret = stripe_keys["endpoint_secret"]
  try:
    event = stripe.Webhook.construct_event(
      payload, sig_header, endpoint_secret
    )
  except ValueError:
    log(user=current_user, request=request, description='Invalid stripe payload')
    return "Invalid payload", 400
  except stripe.error.SignatureVerificationError:
    log(user=current_user, request=request, description='Invalid stripe signature')
    return "Invalid signature", 400

  # Handle the event
  
  if event["type"] == "checkout.session.completed":
    session = event["data"]["object"]
    user_id = session["client_reference_id"]
    customer_id = session["customer"]
    subscription_id = session["subscription"]
    user = db.session.get(User, UUID(user_id))
    if user.stripe:
      user.stripe.stripe_customer_id=customer_id
      user.stripe.stripe_subscription_id=subscription_id
      user.stripe.active=True
      db.session.commit()
      log(user=current_user, request=request, description='Resubscribed via stripe')
    else:
      customer = StripeCustomer(
        user=user,
        stripe_customer_id=customer_id,
        stripe_subscription_id=subscription_id,
        active=True
      )
      db_add(customer)
      log(user=current_user, request=request, description='Subscribed via stripe')
  
  elif event["type"] == "customer.subscription.deleted":
    session = event["data"]["object"]
    customer_id = session["customer"]
    customer = db.session.scalar(
      db.select(StripeCustomer).where(StripeCustomer.stripe_customer_id == customer_id)
    )
    customer.active=False
    log(user=current_user, request=request, description='Unsubscribed via stripe')
    db.session.commit()

  return "", 200
