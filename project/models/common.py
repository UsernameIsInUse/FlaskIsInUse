from project.extensions import db

from sqlalchemy.orm import Mapped, mapped_column
import json
from datetime import datetime, timezone
from typing import Optional

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