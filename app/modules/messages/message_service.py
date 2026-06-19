# Global imports
import logging
from typing import Sequence
# Local imports
from app.modules.messages.message_model import Message
from app.modules.messages.message_repository import MessageRepository
from app.modules.messages.message_schema import MessageCreate

logger = logging.getLogger(__name__)

class MessageService:
    def __init__(self, repo: MessageRepository):
        self.repo = repo

    # ---------- Creating/sending a new message ----------- #
    async def insert_message(self, message: MessageCreate, sender_id: int, room_id: int) -> Message:
        logger.info(f"Service: Sender with ID: {sender_id} inserting a message in room with ID: {room_id}")
        message_data = Message(
            **message.model_dump(),
            sender_id=sender_id,
            room_id=room_id
        )
        new_message = await self.repo.insert(message_data)
        logger.info(f"Service: Sender with ID: {sender_id} successfully inserted a message in room with ID: {room_id}")
        return new_message

    # ---------- Getting all the sent messages (upto 50) ---------- #
    async def get_all_sent_messages_by_room_id(self, room_id: int, limit: int=50) -> Sequence[Message]:
        logger.info(f"Service: Fetching the last 50 messages sent to room with ID: {room_id}")
        sent_messages = await self.repo.find_all_past_messages_by_room_id(room_id, limit)
        logger.info(f"Service: Successfully fetched {len(sent_messages)} messages from room with ID: {room_id}")
        return sent_messages
