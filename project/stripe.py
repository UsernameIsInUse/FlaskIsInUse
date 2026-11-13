import stripe
from dotenv import load_dotenv
from os import environ

load_dotenv(override=True)

stripe_keys = {
  "secret_key":environ['STRIPE_SECRET_KEY'],
  "publishable_key":environ['STRIPE_PUBLIC_KEY'],
  "monthly_price": environ['MONTHLY_PRICE_ID'],
  "yearly_price": environ['YEARLY_PRICE_ID'],
  "endpoint_secret": environ['STRIPE_ENDPOINT_SECRET']
}

stripe_client = stripe.StripeClient(stripe_keys["secret_key"])
