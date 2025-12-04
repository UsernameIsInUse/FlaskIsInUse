from flask import Blueprint, abort, redirect, url_for, request
from project import admin, db
from project.models import *
from flask_admin.contrib.sqla import ModelView
from flask_admin.menu import MenuLink
from flask_admin import AdminIndexView
from flask_login import current_user
from project.access_control import login_redirect, is_admin

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
    return current_user.is_authenticated and is_admin()
  def inaccessible_callback(self, name, **kwargs):
    if current_user.is_authenticated:
      return abort(403)
    return login_redirect()
  
class UserView(CustomBaseModelView):
  column_list = ['email', 'confirmed', 'roles', 'profile', 'groups', 'date_created']
  column_searchable_list = ['email']
  form_columns = ['email', 'confirmed']
  can_delete = False

class ProfileView(CustomBaseModelView):
  column_list = ['username', 'owner', 'group', 'users', 'date_created']
  column_searchable_list = ['username']
  form_columns = ['owner']
  can_delete = False
  
class RoleView(CustomBaseModelView):
  column_list = ['name', 'users', 'date_created']
  column_searchable_list = ['name']
  
class GroupView(CustomBaseModelView):
  column_list = ['name', 'profile', 'users', 'date_created']
  column_searchable_list = ['name']
  can_edit = False
  can_delete = False
  
class LogView(CustomBaseModelView):
  column_list = ['user', 'description', 'date_created']
  column_searchable_list = ['description']

admin.add_view(UserView(User, db.session, category="Users"))
admin.add_view(ProfileView(Profile, db.session, category="Users"))
admin.add_view(RoleView(Role, db.session, category="Users"))
admin.add_view(GroupView(Group, db.session, category="Users"))
admin.add_view(LogView(Log, db.session, category="Utils"))
