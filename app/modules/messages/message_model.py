# Global imports
from datetime import datetime, timezone
from typing import TYPE_CHECKING
from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship
# Local imports
from app.core.database import Base

if TYPE_CHECKING:
    from app.modules.users.user_model import User
    from app.modules.rooms.room_model import Room


class Message(Base):
    __tablename__ = 'messages'

    message_id: Mapped[int] = mapped_column(primary_key=True)
    content: Mapped[str] = mapped_column(nullable=False)
    sent_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    # ---------- Relationships --------- #
    sender_id: Mapped[int] = mapped_column(ForeignKey('users.user_id'))
    room_id: Mapped[int] = mapped_column(ForeignKey('rooms.room_id'))

    sender: Mapped["User"] = relationship(back_populates="messages")
    room: Mapped["Room"] = relationship(back_populates="messages")