# Global imports
from typing import Annotated, TYPE_CHECKING
from fastapi import APIRouter, status, Depends, Path, Query
# Local imports
from app.api.dependencies import get_current_user, room_service_dependency, RateLimiter, delete_cache, get_cache, \
    set_cache
from app.modules.rooms.room_schema import RoomResponse, RoomCreate, RoomDelete, RoomUpdate

if TYPE_CHECKING:
    from app.modules.users.user_model import User

router = APIRouter(prefix="/rooms", tags=["Rooms"])

logged_user = Annotated["User", Depends(get_current_user)]

#---------creating room route-------#
# Creating a strict rule for creating rooms: max 5 tries every 60 seconds
creating_room_limiter = RateLimiter(max_requests=5, window_seconds=60)

@router.post("/", response_model=RoomResponse, status_code=status.HTTP_201_CREATED)
async def create_room(
    data: RoomCreate,
    current_user: logged_user,
    service: room_service_dependency
):
    # This tracks how many times rooms are created
    await creating_room_limiter.check_rate_limit(user_id=current_user.user_id)

    new_room = await service.create_room(room=data, creator_id=current_user.user_id)

    # Deleting the old rooms' cache
    all_rooms_key = f"rooms:all:{current_user.user_id}"
    await delete_cache(all_rooms_key)

    return new_room

#----------Deleting room route-------#
# Creating a strict rule for deleting rooms: max 5 tries every 60 seconds
deleting_room_limiter = RateLimiter(max_requests=5, window_seconds=60)

@router.delete("/{room_id}", status_code=status.HTTP_200_OK)
async def delete_room(
    delete_data: RoomDelete,
    current_user: logged_user,
    service: room_service_dependency,
    room_id: int=Path(..., gt=0)
):
    # This tracks how many times rooms are deleted
    await deleting_room_limiter.check_rate_limit(user_id=current_user.user_id)

    await service.delete_room(
        room_id=room_id,
        creator_id=current_user.user_id,
        current_password=delete_data.current_password
    )

    # Deleting the old room's cache
    single_room_key = f"rooms:single:{room_id}"
    await delete_cache(single_room_key)

    #Deleting the all the old rooms to refresh the room list
    all_rooms_key = f"rooms:all:{current_user.user_id}"
    await delete_cache(all_rooms_key)

    return {"message": f"Room has been deleted successfully!"}

#-------update room route------#
# Creating a strict rule for updating rooms: max 5 tries every 60 seconds
updating_room_limiter = RateLimiter(max_requests=5, window_seconds=60)

@router.patch("/{room_id}", response_model=RoomResponse,status_code=status.HTTP_200_OK)
async def update_room(
    update_data: RoomUpdate,
    current_user: logged_user,
    service: room_service_dependency,
    room_id: int=Path(..., gt=0)
):
    # This tracks how many times rooms are updated
    await updating_room_limiter.check_rate_limit(user_id=current_user.user_id)

    updated_room = await service.update_room(
        room_id=room_id,
        creator_id=current_user.user_id,
        current_password=update_data.current_password,
        data=update_data
    )

    # Deleting the old room's cache
    single_room_key = f"rooms:single:{room_id}"
    await delete_cache(single_room_key)

    #Deleting the all the old rooms to refresh the room list
    all_rooms_key = f"rooms:all:{current_user.user_id}"
    await delete_cache(all_rooms_key)

    return updated_room

#-----view a single room details----#
@router.get("/{room_id}", response_model=RoomResponse, status_code=status.HTTP_200_OK)
async def view_room(
    current_user: logged_user,
    service: room_service_dependency,
    room_id: int=Path(..., gt=0)
):
    # Creating a completely unique cache key for this specific room
    cache_key = f"rooms:single:{room_id}"

    # ---- 1. CHECKING CACHE FIRST (Cache Hit - Checking if the data is in Redis already) ---- #
    cached_room = await get_cache(cache_key)
    if cached_room:
        return cached_room # Returns instantly from Redis RAM

    # ---- 2. FETCHING FROM DB (Cache Miss - if the data wasn't inside Redis) ---- #
    # If Redis was empty, fetch the fresh model from the database service
    room_model = await service.get_room_by_room_id(creator_id=current_user.user_id, room_id=room_id)

    # ---- 3. SAVING TO CACHE FOR NEXT TIME ---- #
    # Turn the Pydantic model into a dictionary so json.dumps can read it safely
    room_dict = RoomResponse.model_validate(room_model).model_dump()

    # Save it to Redis for 5 minutes (300 seconds)
    await set_cache(key=cache_key, data=room_dict, expire_seconds=300)

    return room_model

#---------view all the rooms-------#
@router.get("/", response_model=list[RoomResponse], status_code=status.HTTP_200_OK)
async def view_all_rooms(
    current_user: logged_user,
    service: room_service_dependency,
    skip: int = Query(0, ge=0),
    limit: int = 20
):
    safe_limit = min(limit, 100)

    # Creating a completely unique cache key for the rooms
    cache_key = f"rooms:all:{current_user.user_id}:skip:{skip}:limit:{safe_limit}"

    # ---- 1. CHECKING CACHE FIRST (Cache Hit - Checking if the data is in Redis already) ---- #
    cached_room = await get_cache(cache_key)
    if cached_room:
        return cached_room  # Returns instantly from Redis RAM

    # ---- 2. FETCHING FROM DB (Cache Miss - if the data wasn't inside Redis) ---- #
    # If Redis was empty, fetch the fresh model from the database service
    room_model = await service.get_all_rooms(
        creator_id=current_user.user_id,
        skip=skip,
        limit=safe_limit
    )

    # ---- 3. SAVING TO CACHE FOR NEXT TIME ---- #
    # Turn the Pydantic model into a dictionary so json.dumps can read it safely
    room_list_dict = [RoomResponse.model_validate(room).model_dump() for room in room_model]

    # Save it to Redis for 5 minutes (300 seconds)
    await set_cache(key=cache_key, data=room_list_dict, expire_seconds=300)

    return room_model