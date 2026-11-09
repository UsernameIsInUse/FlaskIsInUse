from flask import Blueprint

bp = Blueprint('views', __name__)

from project.views import home, utils, profile, errors, user, stripe, auth

