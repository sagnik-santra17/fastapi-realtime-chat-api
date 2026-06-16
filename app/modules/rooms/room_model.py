#Global imports
from datetime import datetime, timezone
from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime, ForeignKey
#Local imports
from app.core.database import Base

if TYPE_CHECKING:
    from app.modules.users.user_model import User


class Room(Base):
    __tablename__ = 'chat_rooms'

    room_id: Mapped[int] = mapped_column(primary_key=True)
    room_name: Mapped[str] = mapped_column(unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    #------------relationships----------#
    creator_id: Mapped[int] = mapped_column(ForeignKey('users.user_id'))
    owner: Mapped["User"] = relationship(back_populates="chat_rooms")
