#global imports
from datetime import datetime, timezone
from typing import TYPE_CHECKING
from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
#local imports
from app.core.database import Base

if TYPE_CHECKING:
    from app.modules.rooms.room_model import Room


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    #----------Relationships----------#
    chat_rooms: Mapped[list["Room"]] = relationship(back_populates="owner")
