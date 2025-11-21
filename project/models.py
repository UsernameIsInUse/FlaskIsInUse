from project.extensions import db
from sqlalchemy.sql import func
from project.utils import log
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import json
from flask import url_for
from flask_authorize import AllowancesMixin

class User(UserMixin, db.Model):
  __tablename__ = 'users'
  id = db.Column(db.Integer, primary_key=True)
  
  # local auth
  email = db.Column(db.String(255), unique=True, nullable=False)
  hashed_pass = db.Column(db.String(255), nullable = False)
  
  # oauth
  oauth_accounts = db.relationship("OAuthAccount", backref="user", lazy=True)
  
  # user data / settings
  date_created = db.Column(db.DateTime, nullable=True, default=func.now())
  confirmed = db.Column(db.Boolean, default=False) # Currently unused
  date_confirmed = db.Column(db.DateTime, nullable=True) # Currently unused
  profile_links = db.relationship("UserPortfolio", back_populates="user")
  tos = db.Column(db.Boolean, default=True)
  logs = db.relationship('Log', backref='user', lazy=True)
  
  def __repr__(self):
    return f"{self.email}"

  def set_password(self, password:str):
    log(data={'affected_user':self.email}, description=f'Password Changed for {self.email}')
    self.hashed_pass = generate_password_hash(password)

  def check_password(self, password:str) -> bool:
    return check_password_hash(self.hashed_pass, password)
  
  @property
  def profiles(self) -> list:
    return [link.profile for link in self.profile_links]

class OAuthAccount(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  provider = db.Column(db.String(50), nullable=False)
  provider_user_id = db.Column(db.String(255), nullable=False)
  token = db.Column(db.JSON, nullable=False)
  user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

class Profile(db.Model):
  __tablename__ = 'profiles'
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(64), unique=True, nullable=False)
  date_created = db.Column(db.DateTime, nullable=False, default=func.now())
  users = db.relationship('User', backref='profile', lazy=True)
  user_links = db.relationship("UserPortfolio", back_populates="profile")
  
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

class UserPortfolio(db.Model):
  __tablename__ = 'profile_roles'
  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.ForeignKey("users.id"), nullable=False)
  profile_id = db.Column(db.ForeignKey("profiles.id"), nullable=False)
  user = db.relationship("User", back_populates="profile_links")
  profile = db.relationship("Profile", back_populates="user_links")
  
  permission = db.Column(db.String(50), nullable=False)
  
  date_created = db.Column(db.DateTime, nullable=False, default=func.now())
  
  def __repr__(self):
    return f"{self.profile} - {self.role}"

class Role(db.Model):
  __tablename__ = 'roles'
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(64), unique=True, nullable=False)
  date_created = db.Column(db.DateTime, nullable=False, default=func.now()) 
  profile_links = db.relationship("ProfileRole", back_populates="role")
  
  def __repr__(self):
    return f"{self.name}"
  
class ProfileRole(db.Model):
  __tablename__ = 'profile_roles'
  id = db.Column(db.Integer, primary_key=True)
  profile_id = db.Column(db.ForeignKey("profiles.id"), nullable=False)
  role_id = db.Column(db.ForeignKey("roles.id"), nullable=False)
  profile = db.relationship("Profile", back_populates="role_links")
  role = db.relationship("Role", back_populates="profile_links")
  date_created = db.Column(db.DateTime, nullable=False, default=func.now())
  
  def __repr__(self):
    return f"{self.profile} - {self.role}"

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