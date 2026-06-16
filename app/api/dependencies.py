#Global imports
import logging
from typing import Annotated, TYPE_CHECKING
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from jose.exceptions import ExpiredSignatureError
from sqlalchemy.ext.asyncio import AsyncSession
#local imports
from app.core.database import get_db
from app.utils.user_utils import invalid_credentials
from app.core.config import settings

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from app.modules.users.user_repository import UserRepository
    from app.modules.users.user_service import UserService
    from app.modules.users.user_model import User


db_dependency = Annotated[AsyncSession, Depends(get_db)]

def get_user_service(db: db_dependency) -> "UserService":
    from app.modules.users.user_repository import UserRepository
    from app.modules.users.user_service import UserService
    repo = UserRepository(db)
    return UserService(repo)

user_service_dependency = Annotated["UserService", Depends(get_user_service)]







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