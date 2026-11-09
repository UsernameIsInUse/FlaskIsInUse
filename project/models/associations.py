from project.extensions import db

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Uuid
from datetime import datetime, timezone
import uuid

from typing import TYPE_CHECKING
if TYPE_CHECKING:
  from project.models import User, Profile, Role

class UserProfile(db.Model):
  __tablename__ = 'user_profiless'
  id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid7)
  user_id: Mapped[int] = mapped_column(db.ForeignKey("users.id"))
  profile_id: Mapped[int] = mapped_column(db.ForeignKey("profiles.id"))
  user: Mapped["User"] = db.relationship(back_populates="profile_links")
  profile: Mapped["Profile"] = db.relationship(back_populates="user_links")
  date_created: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
  
  owner: Mapped[bool] = mapped_column(default=False)
  
  def __repr__(self):
    return f"{self.user} - {self.profile}"
  
class UserRole(db.Model):
  __tablename__ = 'user_roles'
  id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid7)
  user_id: Mapped[int] = mapped_column(db.ForeignKey("users.id"))
  role_id: Mapped[int] = mapped_column(db.ForeignKey("roles.id"))
  user: Mapped["User"] = db.relationship(back_populates="role_links")
  role: Mapped["Role"] = db.relationship(back_populates="user_links")
  date_created: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
  
  def __repr__(self):
    return f"{self.user} - {self.role}"