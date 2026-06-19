# Global imports
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class MessageCreate(BaseModel):
    content: str = Field(..., min_length=1)

class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    content: str
    message_id: int
    sender_id: int
    room_id: int
    sent_at: datetime