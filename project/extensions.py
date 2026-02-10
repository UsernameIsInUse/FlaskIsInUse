from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
class Base(DeclarativeBase):
  pass
db = SQLAlchemy(model_class=Base)

from flask_migrate import Migrate
migrate = Migrate(render_as_batch=True)

from flask_login import LoginManager
login = LoginManager()

from flask_wtf import CSRFProtect
csrf = CSRFProtect()

from flask_authorize import Authorize
authorize = Authorize()

from flask_admin import Admin
from flask_admin import AdminIndexView
from flask_login import current_user
from flask import redirect, url_for, request, abort

class MyAdminIndexView(AdminIndexView):
  def is_visible(self):
    return False
  def is_accessible(self):
    return current_user.is_authenticated and current_user.is_admin
  def inaccessible_callback(self, name, **kwargs):
    if current_user.is_authenticated:
      return abort(403)
    return redirect(url_for('views.login', next=request.full_path))
    
  
admin = Admin(name="Admin", url="/admin/", index_view=MyAdminIndexView())

from flask_ipban import IpBan
ipban = IpBan()

from flask_flashy import Flashy
flashy = Flashy()

from flask_squeeze import Squeeze
squeeze = Squeeze()

from flask_debugtoolbar import DebugToolbarExtension
toolbar = DebugToolbarExtension()

from flask_mail import Mail
mail = Mail()

from flask_smorest import Api
api = Api()