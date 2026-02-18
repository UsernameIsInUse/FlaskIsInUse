from flask import url_for
from flask_authorize import PermissionsMixin

from project.extensions import db

from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, timezone
from typing import List

from typing import TYPE_CHECKING
if TYPE_CHECKING:
  from project.models import UserGroup

class Group(db.Model):
  __tablename__ = 'groups'
  id: Mapped[int] = mapped_column(primary_key=True)
  name: Mapped[str] = mapped_column(db.String(255), unique=True)
  date_created: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
  user_links: Mapped[List["UserGroup"]] = db.relationship("UserGroup", back_populates="group", cascade="all, delete-orphan")
  
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