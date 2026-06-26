# Global imports
import json
import logging
import redis.asyncio as aioredis
from fastapi import APIRouter, status, Query, WebSocket, WebSocketDisconnect, HTTPException
from jose import jwt, JWTError

# Local imports
from app.api.dependencies import message_service_dependency, RateLimiter
from app.core.config import settings
from app.modules.messages.message_schema import MessageResponse, MessageCreate
from app.modules.messages.connection_manager import manager

router = APIRouter(prefix="/messages", tags=["Messages"])

logger = logging.getLogger(__name__)

# ----------- Sending/creating a new message --------- #
# Creating a strict rule for sending message: max 5 tries every 10 seconds
send_message_limiter = RateLimiter(max_requests=5, window_seconds=10)

@router.post("/", response_model= MessageResponse, status_code=status.HTTP_201_CREATED)
async def create_message(
    message: MessageCreate,
    service: message_service_dependency,
    sender_id: int,
    room_id: int,
):
    # This tracks how many times messages are sent
    await send_message_limiter.check_rate_limit(user_id=sender_id)

    return await service.insert_message(message=message, sender_id=sender_id, room_id=room_id)

# ---------- Getting the last messages ------ #
@router.get("/", response_model= list[MessageResponse], status_code=status.HTTP_200_OK)
async def get_messages(room_id: int, service: message_service_dependency, limit: int=50):
    return await service.get_all_sent_messages_by_room_id(room_id, limit)

# --------- WebSocker Router ------- #
# Creating a strict rule websocket: max 5 tries every 10 seconds
ws_limiter = RateLimiter(max_requests=5, window_seconds=10)

@router.websocket("/ws/{room_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    room_id: int,
    service: message_service_dependency,
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

    # If the token is perfect, connect them to the room!
    await manager.connect(room_id=room_id, websocket=websocket)
    logger.info(f"User {user_id} successfully connected live to room {room_id}")

    # -------- Keep line open: Wait for incoming messages and share them with the room -------- #
    # Connecting to Redis
    redis_client = aioredis.from_url("redis://localhost:6379", decode_responses=True, protocol=2)
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

            # Packing the REAL user data into a dictionary
            real_chat = {
                "user_id": user_id,
                "room_id": room_id,
                "text": data
            }

            # Turning the dictionary into a JSON string
            json_str = json.dumps(real_chat)

            # Shouting the real message into Redis
            await redis_client.publish("room:messages", json_str)

    except WebSocketDisconnect:
        # If the user closes their browser tab, the line breaks and server gets disconnected
        manager.disconnect(room_id=room_id, websocket=websocket)
        logger.info(f"User {user_id} disconnected from room {room_id}")