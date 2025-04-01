from project.extensions import db
from sqlalchemy.sql import func
from project.utils import log
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import json
from flask import url_for

class User(UserMixin, db.Model): # TODO: Add Multipass, Email Confirmation, 2FA
  __tablename__ = 'users'
  id = db.Column(db.Integer, primary_key=True)
  email = db.Column(db.String(255), unique=True, nullable=False)
  hashed_pass = db.Column(db.String(255), nullable = False)
  date_created = db.Column(db.DateTime, nullable=True, default=func.now())
  confirmed = db.Column(db.Boolean, default=False)
  date_confirmed = db.Column(db.DateTime, nullable=True)
  profile_id = db.Column(db.Integer, db.ForeignKey('profiles.id'))
  tos = db.Column(db.Boolean, default=True)
  logs = db.relationship('Log', backref='user', lazy=True)
  
  def __repr__(self):
    return f"{self.email}"

  def set_password(self, password:str):
    log(data={'affected_user':self.email}, description=f'Password Changed for {self.email}')
    self.hashed_pass = generate_password_hash(password)

  def check_password(self, password:str) -> bool:
    return check_password_hash(self.hashed_pass, password)  
  
class Profile(db.Model): # TODO: Add role-based permissions
  __tablename__ = 'profiles'
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(64), unique=True, nullable=False)
  date_created = db.Column(db.DateTime, nullable=False, default=func.now())
  users = db.relationship('User', backref='profile', lazy=True)
  role_links = db.relationship("ProfileRole", back_populates="profile")
  # Other profile data
  
  def __repr__(self):
    return f"{self.username}"
  
  @property
  def is_admin(self) -> bool:
    for link in self.role_links:
      if link.role.name == 'Admin':
        return True
    return False
  
  @property
  def url(self) -> str:
    return url_for('views.profile', username=self.username)

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