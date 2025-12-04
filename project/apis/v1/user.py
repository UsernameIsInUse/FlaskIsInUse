from flask_smorest import Blueprint
from marshmallow import Schema, validates, ValidationError, fields
from flask.views import MethodView
from project.models import User
from flask_login import login_required, current_user
from flask import abort, render_template, url_for
from project import db
from project.utils import send_email
from flask_flashy import flash


bp = Blueprint(
    "users_v1",
    __name__,
    url_prefix="/api/v1/users"
)
