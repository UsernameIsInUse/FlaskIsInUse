from flask_login import UserMixin
from flask_authorize import AllowancesMixin

from project.extensions import db
from project.utils import log
from project.access_control import is_admin
from project.stripe import stripe

from sqlalchemy.orm import Mapped, mapped_column
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone
from typing import List, Optional

from typing import TYPE_CHECKING
if TYPE_CHECKING:
  from project.models import Log, UserGroup, UserRole

class User(UserMixin, db.Model):
  __tablename__ = 'users'
  id: Mapped[int] = mapped_column(primary_key=True)
  date_created: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
  logs: Mapped[List["Log"]] = db.relationship(backref='user', lazy=True)
  email: Mapped[str] = mapped_column(db.String(255), unique=True)
  
  # local auth
  hashed_pass: Mapped[Optional[str]] = mapped_column(db.String(255))
  unconfirmed_email: Mapped[Optional[str]] = mapped_column(db.String(255))
  confirmed: Mapped[bool] = mapped_column(default=False)
  date_confirmed: Mapped[Optional[datetime]]
  
  # oauth
  oauth_accounts: Mapped[List["OAuthAccount"]] = db.relationship(back_populates="user", cascade="all, delete-orphan")
  
  # permissions
  role_links: Mapped[List["UserRole"]] = db.relationship(back_populates="user")
  group_links: Mapped[List["UserGroup"]] = db.relationship(back_populates="user", cascade="all, delete-orphan")
  
  # user data / settings
  tos: Mapped[bool] = mapped_column(default=True)
  marketing: Mapped[Optional[bool]]
  
  # subscription
  stripe_customers: Mapped[List["StripeCustomer"]] = db.relationship(backref='user', lazy=True, cascade="all, delete-orphan")
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
    from project.models import Profile
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
    
  @property
  def google(self):
    for account in self.oauth_accounts:
      if account.provider == 'google':
        return True
      return False
    
class OAuthAccount(db.Model):
  __tablename__ = "oauth_accounts"
  id: Mapped[int] = mapped_column(primary_key=True)
  user_id: Mapped[int] = mapped_column(db.ForeignKey("users.id"))
  user: Mapped["User"] = db.relationship(back_populates="oauth_accounts")
  
  provider: Mapped[str] = mapped_column(db.String(50), nullable=False)
  provider_user_id: Mapped[str] = mapped_column(db.String(255), nullable=False)
  
  __table_args__ = (
    db.UniqueConstraint("provider", "provider_user_id"),
  )
  
  def __repr__(self):
    return f"{self.user.email}"
  

class Role(db.Model, AllowancesMixin):
  __tablename__ = 'roles'
  __allowances__ = {}
  id: Mapped[int] = mapped_column(primary_key=True)
  name: Mapped[str] = mapped_column(db.String(255), unique=True)
  date_created: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
  user_links: Mapped[List["UserRole"]] = db.relationship(back_populates="role", cascade="all, delete-orphan")
  
  def __repr__(self):
    return f"{self.name}"
  
  @property
  def users(self) -> list:
    return [link.user for link in self.user_links]
  
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
