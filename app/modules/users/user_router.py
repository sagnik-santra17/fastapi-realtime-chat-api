#global imports
from typing import Annotated, TYPE_CHECKING
from fastapi import APIRouter, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
#local imports
from app.api.dependencies import user_service_dependency, get_current_user
from app.modules.users.user_schema import UserResponse, UserCreate, UserLogin, UserUpdate, UserDelete

if TYPE_CHECKING:
    from app.modules.users.user_model import User

router = APIRouter(prefix="/users", tags=["Users"])

current_user = Annotated["User", Depends(get_current_user)]

#----------user sign up router--------------#
@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    data: UserCreate,
    service: user_service_dependency
):
    return await service.create_user(data)

#--------------user log in router-----------#
@router.post("/login", status_code=status.HTTP_200_OK)
async def login(
    service: user_service_dependency,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    user_login_data = UserLogin(
        username=form_data.username,
        password=form_data.password,
    )
    return await service.user_login(user_login_data)

#-------------user delete router------------#
@router.delete("/me", status_code=status.HTTP_200_OK)
async def delete_user(
    data: UserDelete,
    service: user_service_dependency,
    active_user: current_user
):
    await  service.user_delete(user_id=active_user.user_id, delete_data=data)
    return {"detail": "User account deleted successfully"}

#-------------user update router------------#
@router.patch("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def update_user(
    service: user_service_dependency,
    active_user: current_user,
    data: UserUpdate
):
    return await service.user_update(data=data, user_id=active_user.user_id)

#-------------view user details router------------#
@router.get("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def view_user_details(
    service: user_service_dependency,
    active_user: current_user
):
    return await service.check_user_profile(active_user.user_id)
