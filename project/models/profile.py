from flask import url_for

from project.extensions import db

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Uuid
from datetime import datetime, timezone
from typing import List
import uuid

from typing import TYPE_CHECKING
if TYPE_CHECKING:
  from project.models import UserProfile

class Profile(db.Model):
  __tablename__ = 'profiles'
  id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid7)
  username: Mapped[str] = mapped_column(db.String(64), unique=True)
  date_created: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
  user_links: Mapped[List["UserProfile"]] = db.relationship(back_populates="profile")
  
  # Other profile data
  
  def __repr__(self):
    return f"{self.username}"
  
  @property
  def users(self) -> list:
    return [link.user for link in self.user_links]
  
  @property
  def owners(self) -> list:
    return [link.user for link in self.user_links if link.owner]
  
  @property
  def url(self) -> str:
    return url_for('views.profile', username=self.username)