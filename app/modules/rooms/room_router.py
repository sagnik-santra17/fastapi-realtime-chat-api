from typing import Annotated, TYPE_CHECKING
from fastapi import APIRouter, status, Depends, Path, Query

from app.api.dependencies import get_current_user, room_service_dependency
from app.modules.rooms.room_schema import RoomResponse, RoomCreate, RoomDelete, RoomUpdate

if TYPE_CHECKING:
    from app.modules.users.user_model import User

router = APIRouter(prefix="/rooms", tags=["Rooms"])

logged_user = Annotated["User", Depends(get_current_user)]

#---------creating room route-------#
@router.post("/", response_model=RoomResponse, status_code=status.HTTP_201_CREATED)
async def create_room(
    data: RoomCreate,
    current_user: logged_user,
    service: room_service_dependency
):
    return await service.create_room(room=data, creator_id=current_user.user_id)

#----------Deleting room route-------#
@router.delete("/{room_id}", status_code=status.HTTP_200_OK)
async def delete_room(
    delete_data: RoomDelete,
    current_user: logged_user,
    service: room_service_dependency,
    room_id: int=Path(..., gt=0)
):
    await service.delete_room(
        room_id=room_id,
        creator_id=current_user.user_id,
        current_password=delete_data.current_password
    )
    return {"message": f"Room has been deleted successfully!"}

#-------update room route------#
@router.patch("/{room_id}", response_model=RoomResponse,status_code=status.HTTP_200_OK)
async def update_room(
    update_data: RoomUpdate,
    current_user: logged_user,
    service: room_service_dependency,
    room_id: int=Path(..., gt=0)
):
    return await service.update_room(
        room_id=room_id,
        creator_id=current_user.user_id,
        current_password=update_data.current_password,
        data=update_data
    )

#-----view a single room details----#
@router.get("/{room_id}", response_model=RoomResponse, status_code=status.HTTP_200_OK)
async def view_room(
    current_user: logged_user,
    service: room_service_dependency,
    room_id: int=Path(..., gt=0)
):
    return await service.get_room_by_room_id(creator_id=current_user.user_id, room_id=room_id)

#---------view all the rooms-------#
@router.get("/", response_model=list[RoomResponse], status_code=status.HTTP_200_OK)
async def view_all_rooms(
    current_user: logged_user,
    service: room_service_dependency,
    skip: int = Query(0, ge=0),
    limit: int = 20
):
    safe_limit = min(limit, 100)
    return await service.get_all_rooms(
        creator_id=current_user.user_id,
        skip=skip,
        limit=safe_limit
    )