from flask_login import UserMixin

from project.extensions import db
from project.utils import log
from project.stripe import stripe_client

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Uuid, String, ForeignKey
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone
from typing import List, Optional
import uuid

from typing import TYPE_CHECKING
if TYPE_CHECKING:
  from project.models import Log, UserRole, UserProfile

class User(UserMixin, db.Model):
  __tablename__ = 'users'
  id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid7)
  date_created: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
  logs: Mapped[List["Log"]] = db.relationship(backref='user')
  email: Mapped[str] = mapped_column(String(255), unique=True)
    
  # local auth
  hashed_pass: Mapped[Optional[str]]
  unconfirmed_email: Mapped[Optional[str]] = mapped_column(String(255))
  confirmed: Mapped[bool] = mapped_column(default=False)
  date_confirmed: Mapped[Optional[datetime]]
  
  # oauth
  oauth_accounts: Mapped[List["OAuthAccount"]] = db.relationship(back_populates="user", cascade="all, delete-orphan")
  
  # permissions
  role_links: Mapped[List["UserRole"]] = db.relationship(back_populates="user")
  profile_links: Mapped[List["UserProfile"]] = db.relationship(back_populates="user")
  
  # subscription
  stripe: Mapped[Optional["StripeCustomer"]] = db.relationship(backref='user', lazy=True, cascade="all, delete-orphan", single_parent=True)
  pro_override: Mapped[bool] = mapped_column(default=False)
  
  # user data / settings
  tos: Mapped[bool] = mapped_column(default=True)
  marketing: Mapped[Optional[bool]]
  
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
  def profiles(self) -> list:
    return [link.profile for link in self.profile_links]
  
  @property
  def owned_profiles(self) -> list:
    return [link.profile for link in self.profile_links if link.owner]
  
  @property
  def hex(self):
    return self.email.encode("utf-8").hex()
  
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
    
  @property
  def local_auth(self):
    if self.hashed_pass:
      return True
    return False
    
class OAuthAccount(db.Model):
  __tablename__ = "oauth_accounts"
  id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid7)
  date_created: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
  
  user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
  user: Mapped["User"] = db.relationship(back_populates="oauth_accounts")
  
  provider: Mapped[str]
  provider_user_id: Mapped[str]
  
  __table_args__ = (
    db.UniqueConstraint("provider", "provider_user_id"),
  )
  
  def __repr__(self):
    return f"{self.user.email}"

class Role(db.Model):
  __tablename__ = 'roles'
  id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid7)
  date_created: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
  
  user_links: Mapped[List["UserRole"]] = db.relationship(back_populates="role", cascade="all, delete-orphan")
  
  name: Mapped[str] = mapped_column(unique=True)
  
  def __repr__(self):
    return f"{self.name}"
  
  @property
  def users(self) -> list:
    return [link.user for link in self.user_links]
  
class StripeCustomer(db.Model):
  __tablename__ = "stripe_customers"
  id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid7)
  date_created: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
  
  user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('users.id'))
  user: Mapped["User"] = db.relationship(back_populates="stripe")
  
  stripe_customer_id: Mapped[str] = mapped_column(String(255))
  stripe_subscription_id: Mapped[str] = mapped_column(String(255))
  active: Mapped[bool] = mapped_column(default=False)
  
  def __repr__(self) -> str:
    return f"{self.id}"

  @property
  def get_subscription(self):
    try:
      return stripe_client.v1.customers.retrieve(self.stripe_customer_id)
    except:
      return False

  @property
  def get_customer(self):
    try:
      return stripe_client.v1.customers.retrieve(self.stripe_customer_id)
    except:
        return False

  @property
  def get_product(self):
    try:
      return stripe_client.v1.products.retrieve(self.get_subscription.plan.product)
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
