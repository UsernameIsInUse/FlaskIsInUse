from project.extensions import db
from sqlalchemy.sql import func
from project.utils import log
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import json
from flask import url_for
from flask_authorize import PermissionsMixin, AllowancesMixin

class User(UserMixin, db.Model):
  __tablename__ = 'users'
  id = db.Column(db.Integer, primary_key=True)
  date_created = db.Column(db.DateTime, nullable=True, default=func.now())
  logs = db.relationship('Log', backref='user', lazy=True)
  
  # local auth
  email = db.Column(db.String(255), unique=True, nullable=False)
  hashed_pass = db.Column(db.String(255), nullable = False)
  
  # oauth
  
  # permissions
  role_links = db.relationship("UserRole", back_populates="user")
  group_links = db.relationship("UserGroup", back_populates="user")
  
  # user data / settings
  confirmed = db.Column(db.Boolean, default=False) # Currently unused
  date_confirmed = db.Column(db.DateTime, nullable=True) # Currently unused
  tos = db.Column(db.Boolean, default=True)
  
  
  def __repr__(self):
    return f"{self.email}"

  def set_password(self, password:str):
    log(data={'affected_user':self.email}, description=f'Password Changed for {self.email}')
    self.hashed_pass = generate_password_hash(password)

  def check_password(self, password:str) -> bool:
    return check_password_hash(self.hashed_pass, password)
  
  @property
  def roles(self) -> list:
    return [link.role for link in self.role_links]
  
  @property
  def groups(self) -> list:
    return [link.group for link in self.group_links]

class Role(db.Model, AllowancesMixin):
  __tablename__ = 'roles'
  __allowances__ = {}
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(255), unique=True, nullable=False)
  date_created = db.Column(db.DateTime, nullable=False, default=func.now()) 
  user_links = db.relationship("UserRole", back_populates="role")
  
  def __repr__(self):
    return f"{self.name}"
  
class Group(db.Model):
  __tablename__ = 'groups'
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(255), unique=True, nullable=False)
  date_created = db.Column(db.DateTime, nullable=False, default=func.now()) 
  user_links = db.relationship("UserGroup", back_populates="group")
  
  def __repr__(self):
    return f"{self.name}"
  
class UserRole(db.Model):
  __tablename__ = 'user_roles'
  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.ForeignKey("users.id"), nullable=False)
  role_id = db.Column(db.ForeignKey("roles.id"), nullable=False)
  user = db.relationship("User", back_populates="role_links")
  role = db.relationship("Role", back_populates="user_links")
  date_created = db.Column(db.DateTime, nullable=False, default=func.now())
  
  def __repr__(self):
    return f"{self.user} - {self.role}"

class UserGroup(db.Model):
  __tablename__ = 'user_groups'
  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.ForeignKey("users.id"), nullable=False)
  group_id = db.Column(db.ForeignKey("groups.id"), nullable=False)
  user = db.relationship("User", back_populates="group_links")
  group = db.relationship("Group", back_populates="user_links")
  date_created = db.Column(db.DateTime, nullable=False, default=func.now())
  
  def __repr__(self):
    return f"{self.user} - {self.group}"
class Profile(db.Model, PermissionsMixin):
  """Provide a `username` and a `group`
  """
  __tablename__ = 'profiles'
  __permissions__ = dict(
        owner=['read', 'update', 'delete'],
        group=['read', 'update'],
        other=['read']
    )
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(64), unique=True, nullable=False)
  date_created = db.Column(db.DateTime, nullable=False, default=func.now())
  
  # Other profile data
  
  def __repr__(self):
    return f"{self.username}"
  
  @property
  def users(self) -> list:
    return [link.user for link in self.user_links]
  
  @property
  def is_admin(self) -> bool:
    for role in self.roles:
      if role.name == 'Admin':
        return True
    return False
  
  @property
  def url(self) -> str:
    return url_for('views.profile', username=self.username)
class Log(db.Model):
  __tablename__ = 'logs'
  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
  data = db.Column(db.Text, nullable=True)
  description = db.Column(db.Text, nullable=True)
  date_created = db.Column(db.DateTime, nullable=False, default=func.now()) 
  
  def __repr__(self):
    return f"{self.id}"
  
  @property
  def as_dict(self) -> dict:
    """Converts json data into python dict.

    Returns:
        dict: Dictionary of request and other passed data.
    """
    return json.loads(self.data)