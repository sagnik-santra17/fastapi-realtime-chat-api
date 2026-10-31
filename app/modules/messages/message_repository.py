# Global imports
import logging
from typing import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# Local imports
from app.modules.messages.message_model import Message
from app.modules.users.user_model import User 

logger = logging.getLogger(__name__)

class MessageRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ------------ Creating a new message ---------- #
    async def insert(self, message: Message) -> Message:
        logger.info(
            f"Database: Attempting to insert a message from user {message.sender_id} into room {message.room_id}"
        )
        self.db.add(message)
        await self.db.commit()
        await self.db.refresh(message)
        logger.info(f"Database: Successfully created message with ID: {message.message_id}")
        return message

    # --------- Getting all past messages by room id --------- #
    async def find_all_past_messages_by_room_id(self, room_id: int, limit: int=50) -> Sequence[Message]:
        logger.info(f"Database: Fetching up to {limit} past messages for room ID: {room_id}")
        
        stmt = (
            select(Message, User.username) # <-- ADDED User.username
            .join(User, Message.sender_id == User.user_id) # <-- ADDED JOIN
            .where(Message.room_id == room_id)
            .order_by(Message.sent_at.desc()) 
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        rows = result.all()
        
        messages = []
        for msg, username in rows:
            msg.username = username # <-- Dynamically attach username
            messages.append(msg)
            
        messages.reverse() # <-- REVERSE so oldest is first
        
        logger.info(f"Database: Successfully retrieved {len(messages)} past messages for room ID: {room_id}")
        return messages