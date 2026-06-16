#global imports
import logging
from typing import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
#local imports
from app.modules.rooms.room_model import Room
from app.modules.users.user_model import User

logger = logging.getLogger(__name__)

class RoomRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    #--------Creating room-------#
    async def create(self, room: Room) -> Room:
        logger.info(f"Database: Attempting to create a new chatroom with the room name: {room.room_name}")
        self.db.add(room)
        await self.db.commit()
        await self.db.refresh(room)
        logger.info(f"Database: Chatroom successfully created with room id: {room.room_id}")
        return room

    #---------Delete room---------#
    async def delete(self, room: Room) -> None:
        logger.info(f"Database: Attempting to delete a chatroom with the room id: {room.room_id}")
        await self.db.delete(room)
        await self.db.commit()
        logger.info(f"Database: Chatroom successfully deleted with room id: {room.room_id}")

    #---------update room----------#
    async def update(self, room: Room) -> Room:
        logger.info(f"Database: Attempting to update a chatroom with the room id: {room.room_id}")
        await self.db.commit()
        await self.db.refresh(room)
        logger.info(f"Database: Room successfully updated with room id: {room.room_id}")
        return room

    #---------get room by room id--------#
    async def find_room_by_room_id(self, room_id: int) -> Room | None:
        logger.info(f"Database: Fetching expense by ID: {room_id}")
        stmt = select(Room).where(Room.room_id == room_id)
        result = await self.db.execute(stmt)
        room = result.scalar_one_or_none()

        if room is None:
            logger.info(f"Database: No room found for ID: {room_id}")
        return room

    #---------get room by room name----------#
    async def find_room_by_room_name(self, room_name: str) -> Room | None:
        logger.info(f"Database: Fetching expense by name: {room_name}")
        stmt = select(Room).where(Room.room_name == room_name)
        result = await self.db.execute(stmt)
        room = result.scalar_one_or_none()

        if room is None:
            logger.info(f"Database: No room found for name: {room_name}")
        return room

    #---------get all chat rooms------------#
    async def find_all_rooms(self, skip: int=0, limit: int=20) -> Sequence[Room]: #added offset and limit
        logger.info("Database: Fetching all rooms")
        stmt = select(Room).order_by(Room.room_id).limit(limit).offset(skip)
        result = await self.db.execute(stmt)
        rooms = result.scalars().all()

        if not rooms:
            logger.info("Database: No rooms found")
        return rooms

    #---------find creator with room_creator_id----------#
    async def find_creator_with_room_creator_id(self, creator_id: int) -> User | None:
        logger.info(f"Database: Fetching creator data with creator id: {creator_id}")
        stmt = select(User).where(User.user_id == creator_id)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()

        if user is None:
            logger.info(f"Database: No user found for creator id: {creator_id}")
        return user






