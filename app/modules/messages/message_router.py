# Global imports
import json
import logging
import redis.asyncio as aioredis
from fastapi import APIRouter, Depends, status, Query, WebSocket, WebSocketDisconnect, HTTPException
from jose import jwt, JWTError
from sqlalchemy import select 

# Local imports
from app.api.dependencies import get_current_user, message_service_dependency, RateLimiter, delete_cache, get_cache, set_cache
from app.core.config import settings
from app.core.database import AsyncSessionLocal 
from app.modules.messages.message_schema import MessageResponse, MessageCreate
from app.modules.messages.connection_manager import manager
from app.modules.users.user_model import User 

router = APIRouter(prefix="/messages", tags=["Messages"])

logger = logging.getLogger(__name__)

# ----------- Sending/creating a new message --------- #
# Creating a strict rule for sending message: max 5 tries every 10 seconds
send_message_limiter = RateLimiter(max_requests=5, window_seconds=10)

@router.post("/", response_model= MessageResponse, status_code=status.HTTP_201_CREATED)
async def create_message(
    message: MessageCreate,
    service: message_service_dependency,
    room_id: int,
    current_user: dict = Depends(get_current_user)
):
    # Extracting the TRUE sender_id from the verified token payload
    sender_id = int(current_user["user_id"]) if isinstance(current_user, dict) else current_user.user_id

    # This tracks how many times messages are sent
    await send_message_limiter.check_rate_limit(user_id=sender_id)

    new_message = await service.insert_message(message=message, sender_id=sender_id, room_id=room_id)

    # Inject the username into the response before returning
    response = MessageResponse.model_validate(new_message)
    response.username = current_user.username

    # Deleting the old message cache
    all_rooms_key = f"messages:room:{room_id}:*"
    await delete_cache(all_rooms_key)

    return response

# ---------- Getting the last messages ------ #
@router.get("/", response_model= list[MessageResponse], status_code=status.HTTP_200_OK)
async def get_messages(
    room_id: int, 
    service: message_service_dependency, 
    limit: int=50,
    current_user: dict = Depends(get_current_user)
):

    # Creating a completely unique cache key using room_id and limit
    cache_key = f"messages:room:{room_id}:limit:{limit}"

    # ---- 1. CHECKING CACHE FIRST (Cache Hit) ---- #
    cached_messages = await get_cache(cache_key)
    if cached_messages is not None:
        return cached_messages  # Returns list instantly from Redis RAM

    # ---- 2. FETCHING FROM DB (Cache Miss) ---- #
    messages_model = await service.get_all_sent_messages_by_room_id(room_id, limit)

    # ---- 3. SAVING TO CACHE FOR NEXT TIME ---- #
    # Loop through the message list to validate and dump each model safely
    message_list_dict = [MessageResponse.model_validate(msg).model_dump(mode="json") for msg in messages_model]

    # Save it to Redis for 5 minutes (300 seconds)
    await set_cache(key=cache_key, data=message_list_dict, expire_seconds=300)

    return messages_model


# --------- WebSocket Router ------- #
# Creating a strict rule websocket: max 5 tries every 10 seconds
ws_limiter = RateLimiter(max_requests=5, window_seconds=10)

@router.websocket("/ws/{room_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    room_id: int,
    token: str=Query(...)
) -> None:
    logger.info(f"WebSocket connection attempt tracking for room_id: {room_id}")

    try:
        # Decoding the token using SECRET KEY and ALGORITHM
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        # Extracting the user id from payload
        user_id = payload.get("sub")
        if user_id is None:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            logger.warning(f"Connection rejected: No user_id found in token for room_id: {room_id}")
            return
        user_id = int(user_id)

    except JWTError:
        # If decoding fails shut down the connection
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        logger.warning(f"Connection rejected: Invalid token for room_id: {room_id}")
        return

    # Fetch the username from the database
    username = f"User {user_id}"
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.user_id == user_id))
        user = result.scalar_one_or_none()
        if user:
            username = str(user.username)

    # If the token is perfect, connect them to the room!
    await manager.connect(room_id=room_id, websocket=websocket)
    logger.info(f"User {user_id} successfully connected live to room {room_id}")

    # -------- Keep line open: Wait for incoming messages and share them with the room -------- #
    # Connecting to Redis
    redis_client = aioredis.from_url(settings.REDIS_URL, decode_responses=True, protocol=2)
    
    try:
        while True:
            # Stop and wait here until the user types a message and hits send
            data = await websocket.receive_text()

            # Checking if the user is spamming
            try:
                await ws_limiter.check_rate_limit(user_id=user_id)

            except HTTPException:
                # If it's a spam, catch the error and send a private warning text
                await websocket.send_text("System: You are typing too fast! Message not sent.")
                continue  # Skip the lines below and jump back to the start of the loop

            # 1. Parse the incoming JSON from the frontend
            try:
                incoming_payload = json.loads(data)
                message_content = incoming_payload.get("content", "")
            except json.JSONDecodeError:
                message_content = data # Fallback in case plain text is sent

            # 2. Pack the REAL user data into a dictionary
            real_chat = {
                "user_id": user_id,
                "username": username,
                "room_id": room_id,
                "content": message_content
            }

            # Turning the dictionary into a JSON string
            json_str = json.dumps(real_chat)

            # 3. Shouting the real message into Redis (for the database worker)
            await redis_client.publish("room:messages", json_str)

            # Clear the history cache so the next person who joins gets fresh data from the DB
            all_messages_key = f"messages:room:{room_id}:*"
            await delete_cache(all_messages_key)

            # 4. Broadcasting the message to everyone connected to this room!
            await manager.broadcast(room_id, json_str)

    except WebSocketDisconnect:
        # If the user closes their browser tab, the line breaks and server gets disconnected
        logger.info(f"User {user_id} disconnected from room {room_id}")
        
    finally:
        # CRITICAL: Always disconnect and cleanup, no matter how the loop exits
        manager.disconnect(room_id=room_id, websocket=websocket)
        await redis_client.close()