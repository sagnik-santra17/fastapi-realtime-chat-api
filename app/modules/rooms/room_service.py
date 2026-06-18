#global imports
import logging
from typing import Sequence
from fastapi import HTTPException, status
#local imports
from app.core.security import verify_password
from app.modules.rooms.room_repository import RoomRepository
from app.modules.rooms.room_schema import RoomCreate, RoomUpdate
from app.modules.rooms.room_model import Room
from app.utils.room_utils import check_valid_room, check_valid_room_with_creator_id
from app.utils.user_utils import invalid_credentials

logger = logging.getLogger(__name__)

class RoomService:
    def __init__(self, repo: RoomRepository):
        self.repo = repo

    #------------creating a new chatroom----------#
    async def create_room(self, room: RoomCreate, creator_id: int) -> Room:
        logger.info(f"Service: User {creator_id} creating room: {room.room_name}")

        existing_room = await self.repo.find_room_by_room_name(room.room_name)
        if existing_room:
            logger.warning(f"Service: Room creation failed. Name '{room.room_name}' already exists.")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This room name is already taken. Try another one."
            )

        room_data = Room(
            **room.model_dump(),
            creator_id=creator_id
        )
        new_room = await self.repo.create(room_data)
        logger.info(f"Service: User {creator_id} successfully created the room: {room.room_name}")
        return new_room

    #----------Delete a new chatroom-------#
    async def delete_room(self, room_id: int, creator_id: int, current_password: str) -> None:
        logger.info(f"Service: User {creator_id} deleting room: {room_id}")

        room = await self.repo.find_room_by_room_id(room_id)
        valid_room = check_valid_room(room)
        check_valid_room_with_creator_id(room_creator_id=valid_room.creator_id, creator_id=creator_id)

        #------matching passwords to delete---------#
        creator = await self.repo.find_creator_with_room_creator_id(valid_room.creator_id)
        if not verify_password(plain_password=current_password, hashed_password=creator.hashed_password):
            return invalid_credentials()

        await self.repo.delete(valid_room)
        logger.info(f"Service: User {creator_id} successfully deleted the room: {room_id}")
        return None

    #----------update a new chatroom-------#
    async def update_room(self, room_id: int, creator_id: int, current_password: str, data: RoomUpdate) -> Room:
        logger.info(f"Service: User {creator_id} updating room: {room_id}")

        room = await self.repo.find_room_by_room_id(room_id)
        valid_room = check_valid_room(room)
        check_valid_room_with_creator_id(room_creator_id=valid_room.creator_id, creator_id=creator_id)

        # ------matching passwords to delete---------#
        creator = await self.repo.find_creator_with_room_creator_id(valid_room.creator_id)
        if not verify_password(plain_password=current_password, hashed_password=creator.hashed_password):
            return invalid_credentials()

        update_data = data.model_dump(exclude_unset=True)
        update_data.pop("current_password", None)
        for key, value in update_data.items():
            setattr(valid_room, key, value)

        updated_room = await self.repo.update(valid_room)
        logger.info(f"Service: User {creator_id} successfully updated the room: {room_id}")
        return updated_room

    #---------Get chatroom with chatroom name--------#
    async def get_room_by_room_name(self, creator_id: int, room_name: str) -> Room:
        logger.info(f"Service: User {creator_id} looking for room information of room name: {room_name}")

        room = await self.repo.find_room_by_room_name(room_name)
        valid_room = check_valid_room(room)
        check_valid_room_with_creator_id(room_creator_id=valid_room.creator_id, creator_id=creator_id)
        logger.info(f"Service: User {creator_id} found room information successfully: {room_name}")
        return valid_room

    #---------get room by room id--------#
    async def get_room_by_room_id(self, creator_id: int, room_id: int) -> Room:
        logger.info(f"Service: User {creator_id} looking for room information of room ID: {room_id}")

        room = await self.repo.find_room_by_room_id(room_id)
        valid_room = check_valid_room(room)
        check_valid_room_with_creator_id(room_creator_id=valid_room.creator_id, creator_id=creator_id)
        logger.info(f"Service: User {creator_id} found room information successfully: {room_id}")
        return valid_room

    #---------get all rooms--------#
    async def get_all_rooms(self, creator_id: int, skip:int, limit:int) -> Sequence[Room]:
        logger.info(f"Service: Fetching all rooms with skip: {skip} and limit: {limit}")
        rooms = await self.repo.find_all_rooms(creator_id=creator_id, skip=skip, limit=limit)
        logger.info(f"Service: Successfully fetched all {len(rooms)} rooms")
        return rooms

