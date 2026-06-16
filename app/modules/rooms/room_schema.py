#Global imports
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class RoomCreate(BaseModel):
    room_name: str = Field(min_length=3, max_length=100)

class RoomUpdate(BaseModel):
    room_name: str | None = Field(default=None, min_length=3, max_length=100)
    current_password: str = Field(..., description="Enter your password to update your chatroom")

class RoomResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    room_id: int
    room_name: str
    created_at: datetime

class RoomDelete(BaseModel):
    current_password: str = Field(..., description="Enter your current password to delete this chatroom")

