#Global imports
import logging
import json
from typing import Annotated, TYPE_CHECKING
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from jose.exceptions import ExpiredSignatureError
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as aioredis

#local imports
from app.core.database import get_db
from app.utils.user_utils import invalid_credentials
from app.core.config import settings

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from app.modules.users.user_service import UserService
    from app.modules.users.user_model import User
    from app.modules.rooms.room_service import RoomService
    from app.modules.messages.message_service import MessageService


# ----------- Main Database Dependency ---------- #
db_dependency = Annotated[AsyncSession, Depends(get_db)]

#-------User dependency service injection--------#
def get_user_service(db: db_dependency) -> "UserService":
    from app.modules.users.user_repository import UserRepository
    from app.modules.users.user_service import UserService
    repo = UserRepository(db)
    return UserService(repo)

user_service_dependency = Annotated["UserService", Depends(get_user_service)]

#-------Room dependency service injection--------#
def get_room_service(db: db_dependency) -> "RoomService":
    from app.modules.rooms.room_service import RoomService
    from app.modules.rooms.room_repository import RoomRepository
    repo = RoomRepository(db)
    return RoomService(repo)

room_service_dependency = Annotated["RoomService", Depends(get_room_service)]

# ------- Message dependency service injection-------- #
def get_message_dependency(db: db_dependency) -> "MessageService":
    from app.modules.messages.message_repository import MessageRepository
    from app.modules.messages.message_service import MessageService
    from app.modules.rooms.room_repository import RoomRepository
    from app.modules.users.user_repository import UserRepository

    repo = MessageRepository(db)
    room_repo = RoomRepository(db)
    user_repo = UserRepository(db)
    return MessageService(repo, room_repo, user_repo)

message_service_dependency = Annotated["MessageService", Depends(get_message_dependency)]

#-------Getting the current/logged in user------#
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

async def get_current_user(
        token: Annotated[str, Depends(oauth2_scheme)],
        user_service: user_service_dependency
) -> "User":
    user_id = None

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        user_data = payload.get("sub")
        if user_data is None:
            invalid_credentials()

        user_id = int(user_data)

    except ExpiredSignatureError:
        logger.warning("Security: Attempted access with an expired JWT token.")
        invalid_credentials()

    except JWTError:
        logger.warning("Security: Failed to decode JWT token. Invalid signature or format.")
        invalid_credentials()

    user = await user_service.repo.find_user_by_user_id(user_id)
    if user is None:
        logger.warning(f"Security: Token valid, but user ID {user_id} does not exist.")
        invalid_credentials()
    return user


# ------------- Rate Limiting Tool ------------ #

# Connecting to your existing Redis server
redis_client = aioredis.from_url("redis://localhost:6379", decode_responses=True, protocol=2)

# Reusable class for rate limiting
class RateLimiter:
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds

    async def check_rate_limit(self, user_id: int | str):

        # Creating a unique key for this specific user in Redis
        key = f"rate_limit:user:{user_id}"

        # If the key doesn't exist yet, Redis automatically creates it at 1
        current_request = await redis_client.incr(key)

        if current_request == 1:
            # Uses the custom seconds we passed in
            await redis_client.expire(key, self.window_seconds)

        # If the counter goes past our limit (max_requests), block the request
        if current_request > self.max_requests:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Slow down!"
            )


# ---------- Caching --------- #
# ---- Tool for grabbing the data from the cache ------ #
async def get_cache(key: str):
    cached_data = await redis_client.get(key)
    if cached_data:
        # If data exists, turn the text back into a Python list/dict
        return json.loads(cached_data)
    return None

# ---- Tool to save data into cache ------ #
async def set_cache(key: str, data, expire_seconds: int=60):
    # Turning Python data into a plain text string
    json_string = json.dumps(data)
    # Saving it to Redis and set a timer (defaults to 60 seconds)
    await redis_client.setex(key, expire_seconds, json_string)

# ------ Tool to completely delete a cache key ------ #
async def delete_cache(key: str) -> None:
    await redis_client.delete(key)



