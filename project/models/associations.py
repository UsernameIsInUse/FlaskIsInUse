from project.extensions import db

from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, timezone

from typing import TYPE_CHECKING
if TYPE_CHECKING:
  from project.models import User, Group, Role

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