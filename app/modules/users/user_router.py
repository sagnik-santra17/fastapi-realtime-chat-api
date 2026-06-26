#global imports
from typing import Annotated, TYPE_CHECKING
from fastapi import APIRouter, status, Depends, BackgroundTasks, Request
from fastapi.security import OAuth2PasswordRequestForm
#local imports
from app.api.dependencies import user_service_dependency, get_current_user, RateLimiter
from app.modules.users.user_schema import UserResponse, UserCreate, UserLogin, UserUpdate, UserDelete
from app.modules.users.user_tasks import send_email_notification

if TYPE_CHECKING:
    from app.modules.users.user_model import User

router = APIRouter(prefix="/users", tags=["Users"])

current_user = Annotated["User", Depends(get_current_user)]

#----------user sign up router--------------#
# Creating a strict rule for signup attempts: max 3 tries every 60 seconds
signup_limiter = RateLimiter(max_requests=3, window_seconds=60)

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    data: UserCreate,
    service: user_service_dependency,
    background_tasks: BackgroundTasks,
    request: Request
):
    # This tracks how many times this specific IP Address is being guessed
    await signup_limiter.check_rate_limit(user_id=request.client.host)

    new_user =  await service.create_user(data)

    # Injecting the email notification background task
    background_tasks.add_task(send_email_notification, new_user.email, new_user.username)
    return new_user

#--------------user log in router-----------#
# Creating a strict rule for login attempts: max 5 tries every 60 seconds
login_limiter = RateLimiter(max_requests=5, window_seconds=60)

@router.post("/login", status_code=status.HTTP_200_OK)
async def login(
    service: user_service_dependency,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    # This tracks how many times this specific username is being guessed
    await login_limiter.check_rate_limit(user_id=form_data.username)

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
