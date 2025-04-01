from flask import Blueprint, abort
from project import admin, db
from project.models import *
from flask_admin.contrib.sqla import ModelView
from flask_admin.menu import MenuLink
from flask_login import current_user
from project.utils import is_admin, login_redirect

bp = Blueprint('admin_app', __name__)

admin.add_link(MenuLink(name="Home", url='/'))

class CustomBaseModelView(ModelView):
  page_size = 50
  can_view_details = True
  create_modal = True
  edit_modal = True
  can_delete = True
  can_export = True
  column_default_sort = ('id',True)
  def is_accessible(self):
    return is_admin()
  def inaccessible_callback(self, name, **kwargs):
    if current_user.is_authenticated:
      return abort(403)
    return login_redirect()
  
class UserView(CustomBaseModelView):
  column_list = ['email', 'confirmed', 'profile', 'tos', 'date_created']
  column_searchable_list = ['email']

class ProfileView(CustomBaseModelView):
  column_list = ['username', 'users', 'role_links', 'date_created']
  column_searchable_list = ['username']

class RoleView(CustomBaseModelView):
  column_list = ['name', 'date_created']
  column_searchable_list = ['name']

class ProfileRoleView(CustomBaseModelView):
  column_list = ['profile', 'role', 'date_created']
  
class LogView(CustomBaseModelView):
  column_list = ['user', 'description', 'date_created']
  column_searchable_list = ['description']

admin.add_view(UserView(User, db.session))
admin.add_view(ProfileView(Profile, db.session))
admin.add_view(RoleView(Role, db.session))
admin.add_view(ProfileRoleView(ProfileRole, db.session))
admin.add_view(LogView(Log, db.session))
