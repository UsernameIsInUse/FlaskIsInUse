from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

from flask_migrate import Migrate
migrate = Migrate(render_as_batch=True)

from flask_login import LoginManager
login = LoginManager()

from flask_wtf import CSRFProtect
csrf = CSRFProtect()

from flask_admin import Admin
from flask_admin import AdminIndexView
from flask_login import current_user
from flask import redirect, url_for, request, abort

class MyAdminIndexView(AdminIndexView):
  def is_visible(self):
    return False
  def is_accessible(self):
    return current_user.is_authenticated and current_user.profile.is_admin
  def inaccessible_callback(self, name, **kwargs):
    if current_user.is_authenticated:
      return abort(403)
    return redirect(url_for('views.login', next=request.url))
    
  
admin = Admin(name="Admin", template_mode="bootstrap3", url="/admin/", index_view=MyAdminIndexView())

from flask_ipban import IpBan
ipban = IpBan()

from flask_flashy import Flashy
flashy = Flashy()