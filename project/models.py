from project.extensions import db
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column
from project.utils import log
from project.access_control import is_admin
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import json
from flask import url_for
from flask_authorize import PermissionsMixin, AllowancesMixin
from project.stripe import stripe
from datetime import datetime, timezone
from typing import List, Optional

class User(UserMixin, db.Model):
  __tablename__ = 'users'
  id: Mapped[int] = mapped_column(primary_key=True)
  date_created: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
  logs: Mapped[List["Log"]] = db.relationship(backref='user', lazy=True)
  
  # local auth
  email: Mapped[str] = mapped_column(db.String(255), unique=True)
  hashed_pass: Mapped[str] = mapped_column(db.String(255))
  unconfirmed_email: Mapped[Optional[str]] = mapped_column(db.String(255))
  confirmed: Mapped[bool] = mapped_column(default=False)
  date_confirmed: Mapped[Optional[datetime]]
  
  # oauth
  
  # permissions
  role_links: Mapped[List["UserRole"]] = db.relationship(back_populates="user")
  group_links: Mapped[List["UserGroup"]] = db.relationship(back_populates="user")
  
  # user data / settings
  tos: Mapped[bool] = mapped_column(default=True)
  marketing: Mapped[Optional[bool]]
  
  # subscription
  stripe_customers: Mapped[List["StripeCustomer"]] = db.relationship(backref='user', lazy=True)
  pro_override: Mapped[bool] = mapped_column(default=False)
  
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
  
  @property
  def main_group(self):
    return self.group_links[0].group
  
  @property
  def profile(self):
    return self.main_group.profile
  
  @property
  def profiles(self) -> list:
    profiles = []
    for group in self.groups:
      profiles.append(Profile.query.filter_by(username=group.name).first())
    return profiles
  
  @property
  def is_admin(self):
    return is_admin(self)
  
  @property
  def hex(self):
    return self.email.encode("utf-8").hex()
  
  @property
  def stripe(self):
    try:
      return self.stripe_customers[0]
    except:
      return False
  
  @property
  def is_pro(self) -> bool:
    try:
      if self.pro_override or self.stripe.is_active:
        return True
      return False
    except:
      return False

class Role(db.Model, AllowancesMixin):
  __tablename__ = 'roles'
  __allowances__ = {}
  id: Mapped[int] = mapped_column(primary_key=True)
  name: Mapped[str] = mapped_column(db.String(255), unique=True)
  date_created: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
  user_links: Mapped[List["UserRole"]] = db.relationship(back_populates="role")
  
  def __repr__(self):
    return f"{self.name}"
  
  @property
  def users(self) -> list:
    return [link.user for link in self.user_links]
  
class Group(db.Model):
  __tablename__ = 'groups'
  id: Mapped[int] = mapped_column(primary_key=True)
  name: Mapped[str] = mapped_column(db.String(255), unique=True)
  date_created: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
  user_links: Mapped[List["UserGroup"]] = db.relationship("UserGroup", back_populates="group")
  
  def __repr__(self):
    return f"{self.name}"
  
  @property
  def users(self) -> list:
    return [link.user for link in self.user_links]
  
  @property
  def profile(self):
    return Profile.query.filter_by(username=self.name).first()
  
  @property
  def owner(self):
    return self.profile.owner
  
class UserRole(db.Model):
  __tablename__ = 'user_roles'
  id: Mapped[int] = mapped_column(primary_key=True)
  user_id: Mapped[int] = mapped_column(db.ForeignKey("users.id"))
  role_id: Mapped[int] = mapped_column(db.ForeignKey("roles.id"))
  user: Mapped["User"] = db.relationship(back_populates="role_links")
  role: Mapped["Role"] = db.relationship(back_populates="user_links")
  date_created: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
  
  def __repr__(self):
    return f"{self.user} - {self.role}"

class UserGroup(db.Model):
  __tablename__ = 'user_groups'
  id: Mapped[int] = mapped_column(primary_key=True)
  user_id: Mapped[int] = mapped_column(db.ForeignKey("users.id"))
  group_id: Mapped[int] = mapped_column(db.ForeignKey("groups.id"))
  user: Mapped["User"] = db.relationship(back_populates="group_links")
  group: Mapped["Group"] = db.relationship(back_populates="user_links")
  date_created: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
  
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
  id: Mapped[int] = mapped_column(primary_key=True)
  username: Mapped[str] = mapped_column(db.String(64), unique=True)
  date_created: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
  
  # Other profile data
  
  def __repr__(self):
    return f"{self.username}"
  
  @property
  def users(self) -> list:
    return self.group.users
  
  @property
  def url(self) -> str:
    return url_for('views.profile', username=self.username)
  
class StripeCustomer(db.Model):
  __tablename__ = "stripe_customers"
  id: Mapped[int] = mapped_column(primary_key=True)
  user_id: Mapped[int] = mapped_column(db.ForeignKey('users.id'))
  stripe_customer_id: Mapped[str] = mapped_column(db.String(255))
  stripe_subscription_id: Mapped[str] = mapped_column(db.String(255))
  active: Mapped[bool] = mapped_column(default=False)
  date_created: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
  
  def __repr__(self):
    return f"{self.id}"

  @property
  def get_subscription(self):
    try:
      return stripe.Subscription.retrieve(self.stripe_subscription_id)
    except:
      return False

  @property
  def get_customer(self):
    try:
      return stripe.Customer.retrieve(self.stripe_customer_id)
    except:
        return False

  @property
  def get_product(self):
    try:
      return stripe.Product.retrieve(self.get_subscription.plan.product)
    except:
      return False
  
  @property
  def is_active(self) -> bool:
    try:
      if self.get_subscription.status == "active":
        return True
      return False
    except:
      return False


class Log(db.Model):
  __tablename__ = 'logs'
  id: Mapped[int] = mapped_column(primary_key=True)
  user_id: Mapped[Optional[int]] = mapped_column(db.ForeignKey('users.id'))
  data: Mapped[Optional[str]] = mapped_column(db.Text)
  description: Mapped[Optional[str]] = mapped_column(db.Text)
  date_created: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
  
  def __repr__(self):
    return f"{self.id}"
  
  @property
  def as_dict(self) -> dict:
    """Converts json data into python dict.

    Returns:
        dict: Dictionary of request and other passed data.
    """
    return json.loads(self.data)