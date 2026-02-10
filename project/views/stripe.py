from project.views import bp
from flask import redirect, url_for, request, jsonify, abort
from flask_login import current_user, login_required
from flask_flashy import flash
from project.utils import log
from project.stripe import stripe, stripe_keys
from project.models import User, StripeCustomer
from project.extensions import db, csrf

@bp.route('/subscription/', methods=['POST','GET'])
@login_required
def subscription():
  return redirect(url_for('views.user_settings', page="subscription"))

@bp.route('/subscription/success', methods=['POST','GET'])
@login_required
def subscription_success():
  return redirect(url_for('views.user_settings', page="subscription"))

@bp.route('/subscription/cancel', methods=['POST','GET'])
@login_required
def subscription_cancel():
  return redirect(url_for('views.user_settings', page="subscription"))

@bp.route("/subscription/config")
@login_required
def get_publishable_key():
  stripe_config = {"publicKey": stripe_keys["publishable_key"]}
  return jsonify(stripe_config)
  
@bp.route('/subscription/create-checkout-session/<term>')
@login_required
def create_checkout_session(term):
  log(user=current_user, request=request, description='Created stripe checkout session')
  stripe.api_key = stripe_keys["secret_key"]
  if term == "m":
    line_items=[
        {
          "price": stripe_keys["monthly_price"],
          "quantity": 1,
        }
      ]
  elif term == "y":
    line_items=[
        {
          "price": stripe_keys["yearly_price"],
          "quantity": 1,
        }
      ]
  else:
    abort(400)
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
    return jsonify({"sessionId": checkout_session["id"]})
  except Exception as e:
    return jsonify(error=str(e)), 403
  

@bp.route("/subscription/webhook", methods=["POST"])
@csrf.exempt
def stripe_webhook():
  payload = request.data
  sig_header = request.headers.get("Stripe-Signature")
  try:
    event = stripe.Webhook.construct_event(
      payload, sig_header, stripe_keys["endpoint_secret"]
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
    user = User.query.get(int(user_id))
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
      db.session.add(customer)
      db.session.commit()
      log(user=current_user, request=request, description='Subscribed via stripe')
  
  elif event["type"] == "customer.subscription.deleted":
    session = event["data"]["object"]
    customer_id = session["customer"]
    customer = StripeCustomer.query.filter_by(stripe_customer_id=customer_id).first()
    customer.active=False
    log(user=current_user, request=request, description='Unsubscribed via stripe')
    db.session.commit()

  return "", 200

@bp.route('/subscription/create-portal-session')
@login_required
def create_portal_session():
  stripe.api_key = stripe_keys["secret_key"]
  try:
    portal_session = stripe.billing_portal.Session.create(
      customer = current_user.stripe.stripe_customer_id,
      return_url = url_for('views.user_settings', _external=True)
    )
    log(user=current_user, request=request, description='Created a stripe billing portal session')
    return jsonify({'url': portal_session.url})
  except Exception as e:
    return jsonify({'error': str(e)}), 403
