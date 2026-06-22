# Global imports
import logging
from fastapi import APIRouter, status, Query, WebSocket, WebSocketDisconnect
from jose import jwt, JWTError

# Local imports
from app.api.dependencies import message_service_dependency
from app.core.config import settings
from app.modules.messages.message_schema import MessageResponse, MessageCreate
from app.modules.messages.connection_manager import manager

router = APIRouter(prefix="/messages", tags=["Messages"])

logger = logging.getLogger(__name__)

# ----------- Sending/creating a new message --------- #
@router.post("/", response_model= MessageResponse, status_code=status.HTTP_201_CREATED)
async def create_message(
    message: MessageCreate,
    service: message_service_dependency,
    sender_id: int,
    room_id: int,
):
    return await service.insert_message(message=message, sender_id=sender_id, room_id=room_id)

# ---------- Getting the last messages ------ #
@router.get("/", response_model= list[MessageResponse], status_code=status.HTTP_200_OK)
async def get_messages(room_id: int, service: message_service_dependency, limit: int=50):
    return await service.get_all_sent_messages_by_room_id(room_id, limit)

# --------- WebSocker Router ------- #
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
    try:
        while True:
            # Stop and wait here until the user types a message and hits send
            data = await websocket.receive_text()

            # Inserting the text string into your Pydantic validation schema
            db_message = MessageCreate(content=data)

            # Saving the message permanently to the database
            await service.insert_message(message=db_message, room_id=room_id, sender_id=user_id)

            # As soon as a message arrives, send it out to everyone in the room
            await manager.broadcast(room_id=room_id, message=f"User {user_id}: {data}")

    except WebSocketDisconnect:
        # If the user closes their browser tab, the line breaks and server gets disconnected
        manager.disconnect(room_id=room_id, websocket=websocket)
        logger.info(f"User {user_id} disconnected from room {room_id}")