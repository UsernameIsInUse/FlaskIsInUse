from flask import Blueprint, redirect, url_for, request, abort
from flask_admin.contrib.sqla import ModelView
from flask_admin.menu import MenuLink
from flask_admin import AdminIndexView
from flask_login import current_user

from project import admin, db
from project.models import *
from project.access_control import login_redirect, is_admin

import uuid

bp = Blueprint('admin_app', __name__)

admin.add_link(MenuLink(name="Home", url='/'))

class MyAdminIndexView(AdminIndexView):
  def is_visible(self):
    return False
  def is_accessible(self):
    return current_user.is_authenticated and is_admin()
  def inaccessible_callback(self, name, **kwargs):
    if current_user.is_authenticated:
      return abort(403)
    return login_redirect()

admin.index_view = MyAdminIndexView

class CustomBaseModelView(ModelView):
  page_size = 50
  can_view_details = True
  create_modal = True
  edit_modal = True
  can_delete = True
  can_export = True
  column_default_sort = ('id',True)
  def get_one(self, id):
    if isinstance(id, str):
      id = uuid.UUID(id)
    return self.session.get(self.model, id)
  def is_accessible(self):
    return current_user.is_authenticated and is_admin()
  def inaccessible_callback(self, name, **kwargs):
    if current_user.is_authenticated:
      return abort(403)
    return login_redirect()
  
class UserView(CustomBaseModelView):
  column_list = ['email', 'is_pro', 'confirmed', 'marketing', 'roles', 'profiles', 'oauth_accounts', 'date_created']
  column_searchable_list = ['email']
  form_columns = ['email', 'confirmed', 'pro_override']
  can_delete = False

class ProfileView(CustomBaseModelView):
  column_list = ['username', 'owners', 'users', 'date_created']
  column_searchable_list = ['username']
  can_delete = False
  
class RoleView(CustomBaseModelView):
  column_list = ['name', 'users', 'date_created']
  column_searchable_list = ['name']
  
class StripeView(CustomBaseModelView):
  column_list = ['user','stripe_customer_id','stripe_subscription_id','active']
  column_filters = ['active']
  form_columns = ['active']
  can_delete = False
  
class LogView(CustomBaseModelView):
  column_list = ['user', 'description', 'date_created']
  column_searchable_list = ['description']
  
class OAuthView(CustomBaseModelView):
  column_list = ['user', 'provider']
  column_filters = ['provider']
  
class EmailView(CustomBaseModelView):
  column_list = ['email','marketing']
  column_filters = ['marketing']
  can_create = False
  can_edit = False
  can_delete = False

admin.add_view(UserView(User, db.session, category="Users"))
admin.add_view(OAuthView(OAuthAccount, db.session, category="Users"))
admin.add_view(ProfileView(Profile, db.session, category="Users"))
admin.add_view(RoleView(Role, db.session, category="Users"))
admin.add_view(StripeView(StripeCustomer, db.session, category="Users"))
admin.add_view(LogView(Log, db.session, category="Utils"))
admin.add_view(EmailView(User, db.session, category="Utils", endpoint="user_emails", name="Emails"))
