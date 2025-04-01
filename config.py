from dotenv import load_dotenv
from os import environ
from datetime import timedelta

load_dotenv()

class Config:
  SECRET_KEY = environ['SECRET_KEY']
  SQLALCHEMY_DATABASE_URI = environ['DATABASE_URL']
  SQLALCHEMY_TRACK_MODIFICATIONS = False
  PRESERVE_CONTEXT_ON_EXCEPTION = False
  SESSION_COOKIE_SECURE=True
  SESSION_COOKIE_HTTPONLY=True
  REMEMBER_COOKIE_DURATION = timedelta(days=30)
  SESSION_COOKIE_SAMESITE = 'Lax'
  SECURITY_PASSWORD_SALT = environ['SALT']
  APP_VERSION = "Alpha 0.1.0"
  APP_NAME = "FlaskApp"
  FA = environ['FA']
