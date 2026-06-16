#global imports
from fastapi import HTTPException, status
#local imports
from app.modules.rooms.room_model import Room

#--------Checking if the room exists with the user id---------#
def check_valid_room(room: Room | None) -> Room:
    if room is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found"
        )
    return room

#---------Checking if the room belongs to the creator---------#
def check_valid_room_with_creator_id(room_creator_id: int, creator_id: int) -> bool:
    if room_creator_id != creator_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to do this task"
        )
    return True