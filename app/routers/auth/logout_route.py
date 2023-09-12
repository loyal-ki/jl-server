import redis.asyncio
from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.redis.redis import get_redis
from app.core.redis.user_session_repository import UserSessionRepository
from app.core.schema.base_response import BaseResponse
from app.core.schema.error_schema import Error, ErrorCode
from app.dependencies import get_current_user
from app.repositories.session.user_session_repository_protocol import (
    UserSessionRepositoryProtocol,
)
from app.repositories.user.user_repository import UserRepository
from app.repositories.user.user_repository_protocol import (
    UserRepositoryProtocol,
)
from app.usecases.auth.logout.logout_usecase import (
    LogoutInteractor,
    LogoutUseCase,
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

router = APIRouter(
    prefix="/auth", tags=["auth"], dependencies=[Depends(get_current_user)]
)


def user_repository() -> UserRepositoryProtocol:
    return UserRepository()


def user_session_repository(
    redis: redis.asyncio.Redis = Depends(get_redis),
) -> UserSessionRepositoryProtocol:
    return UserSessionRepository(redis=redis)


def logout_usecase(
    user_repository: UserRepositoryProtocol = Depends(user_repository),
    user_session_repository: UserSessionRepositoryProtocol = Depends(
        user_session_repository
    ),
    session: Session = Depends(get_db),
) -> LogoutUseCase:
    return LogoutInteractor(
        user_repository=user_repository,
        user_session_repository=user_session_repository,
        session=session,
    )


@router.post(
    "/logout",
    summary="Logout",
    status_code=status.HTTP_200_OK,
)
async def signout(
    token: str = Depends(oauth2_scheme),
    logout_usecase: LogoutUseCase = Depends(logout_usecase),
):
    """
    Logout.

    Parameters:
        token (str): The authentication token.
        logout_usecase (LogoutUseCase): The logout use case.

    Returns:
        BaseResponse: The response indicating the success or failure of the logout process.
    """
    try:
        await logout_usecase.logout(token=token)
        return BaseResponse.success()
    except Exception:
        return BaseResponse.failed(Error(ErrorCode.INTERNAL_SERVER_ERROR))
