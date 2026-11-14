from flask import Blueprint

bp = Blueprint('views', __name__, static_folder='../static', static_url_path='/static')

from project.views import home, utils, profile, errors, user, stripe, auth

