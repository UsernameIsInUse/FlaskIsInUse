from project.extensions import db

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, Uuid
import json
from datetime import datetime, timezone
from typing import Optional
import uuid

from typing import TYPE_CHECKING
if TYPE_CHECKING:
  from project.models import User

class Log(db.Model):
  __tablename__ = 'logs'
  id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid7)
  date_created: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
  
  user_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey('users.id'))
  user: Mapped[Optional["User"]] = db.relationship(back_populates="logs")
  
  data: Mapped[Optional[str]]
  description: Mapped[Optional[str]]
  
  def __repr__(self):
    return f"{self.id}"
  
  @property
  def as_dict(self) -> dict:
    """Converts json data into python dict.

    Returns:
        dict: Dictionary of request and other passed data.
    """
    return json.loads(self.data)