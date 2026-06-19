from fastapi import APIRouter, status

from app.api.dependencies import message_service_dependency
from app.modules.messages.message_schema import MessageResponse, MessageCreate

router = APIRouter(prefix="/messages", tags=["Messages"])

# ----------- Sending/creating a new message --------- #
@router.post("/", response_model= MessageResponse, status_code=status.HTTP_201_CREATED)
async def create_message(
    message: MessageCreate,
    service: message_service_dependency,
    sender_id: int,
    room_id: int,
):
    return await service.insert_message(message=message, sender_id=sender_id, room_id=room_id)

@router.get("/", response_model= list[MessageResponse], status_code=status.HTTP_200_OK)
async def get_messages(room_id: int, service: message_service_dependency, limit: int=50):
    return await service.get_all_sent_messages_by_room_id(room_id, limit)
