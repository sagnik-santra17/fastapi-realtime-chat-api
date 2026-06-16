from datetime import datetime
from pydantic import BaseModel, Field, EmailStr, model_validator, ConfigDict


#User create dict
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=20)
    email: EmailStr = Field(...)
    password: str = Field(..., min_length=8, max_length=100)
    confirm_password: str = Field(..., min_length=8, max_length=100)
    is_active: bool = Field(...)

    #Validating password and confirm password while creating user
    @model_validator(mode="after")
    def check_password_match(self):
        if self.password != self.confirm_password:
            raise ValueError("Passwords don't match")
        return  self

#User update dict
class UserUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=3, max_length=20)
    email: EmailStr | None = Field(default=None)
    password: str | None = Field(default=None, min_length=8, max_length=100)
    confirm_password: str | None = Field(default=None, min_length=8, max_length=100)

    current_password: str = Field(..., description="Enter your current password to update your account")

    #Validating password and confirm password while updating the user
    @model_validator(mode="after")
    def check_password_update(self):
        if self.password != self.confirm_password:
            raise ValueError("Passwords don't match")
        if self.password is None and self.confirm_password is not None:
            raise ValueError("You have entered confirm password but not password")
        if self.password is not None and self.confirm_password is None:
            raise ValueError("You have entered password but not confirm password")
        return self

#User out dict
class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: int
    username: str
    email: EmailStr
    is_active: bool
    created_at: datetime


#User login dict
class UserLogin(BaseModel):
    username: str
    password: str

#User delete schema
class UserDelete(BaseModel):
    password: str = Field(..., description="Enter your current password to delete this account")

#User token dict
class Token(BaseModel):
    access_token: str
    token_type: str



