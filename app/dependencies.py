import redis.asyncio
from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

import app.core.exceptions.user.user_exceptions as exception
from app.config.config import Config
from app.core.database import get_db
from app.core.entities.user.user_entity import UserEntity
from app.core.redis.redis import get_redis
from app.core.redis.user_session_repository import UserSessionRepository
from app.core.schema.base_response import BaseResponse
from app.core.schema.common_schemas import ClientSecret
from app.core.schema.error_schema import Error, ErrorCode
from app.repositories.session.user_session_repository_protocol import (
    UserSessionRepositoryProtocol,
)
from app.repositories.user.user_repository import UserRepository
from app.repositories.user.user_repository_protocol import (
    UserRepositoryProtocol,
)
from app.routers.user.get_current_user_usecase import (
    GetCurrentUserInteractor,
    GetCurrentUserUseCase,
)
from app.usecases.auth.check_verification.check_verification_usecase import (
    CheckVerificationInteractor,
    CheckVerificationUseCase,
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def user_repository() -> UserRepositoryProtocol:
    return UserRepository()


def user_session_repository(
    redis: redis.asyncio.Redis = Depends(get_redis),
) -> UserSessionRepositoryProtocol:
    return UserSessionRepository(redis=redis)


def get_current_user_usecase(
    user_repository: UserRepositoryProtocol = Depends(user_repository),
    user_session_repository: UserSessionRepositoryProtocol = Depends(
        user_session_repository
    ),
    session: Session = Depends(get_db),
) -> GetCurrentUserUseCase:
    return GetCurrentUserInteractor(
        user_repository=user_repository,
        user_session_repository=user_session_repository,
        session=session,
    )


def check_verification_usecase(
    user_repository: UserRepositoryProtocol = Depends(user_repository),
    user_session_repository: UserSessionRepositoryProtocol = Depends(
        user_session_repository
    ),
    session: Session = Depends(get_db),
) -> CheckVerificationUseCase:
    return CheckVerificationInteractor(
        user_repository=user_repository,
        user_session_repository=user_session_repository,
        session=session,
    )


async def get_current_user(
    request: Request,
    token: str = Depends(oauth2_scheme),
    get_current_user_usecase: GetCurrentUserUseCase = Depends(
        get_current_user_usecase
    ),
    check_verification_usecase: CheckVerificationUseCase = Depends(
        check_verification_usecase
    ),
) -> UserEntity:
    user = await get_current_user_usecase.get_current_user(token=token)
    if not user or user.deleted_at:
        return BaseResponse.failed(Error(ErrorCode.BAD_TOKEN))

    if (
        (request.method == "POST" and request.url.path == "/auth/logout")
        or (request.method == "GET" and request.url.path == "/users/account")
        or (
            request.method == "POST"
            and request.url.path == "/auth/verify/email/refresh"
        )
        or (
            request.method == "POST"
            and request.url.path == "/auth/verify/phone/refresh"
        )
    ):
        return user

    try:
        verified = await check_verification_usecase.check_verification(
            token=token
        )
    except exception.InvalidToken:
        return BaseResponse.failed(Error(ErrorCode.BAD_TOKEN))
    if not verified:
        return BaseResponse.failed(Error(ErrorCode.NOT_VERIFIED))

    return user


def check_client_credential(form_data: ClientSecret):
    if (
        not form_data.client_id
        or not form_data.client_secret
        or form_data.client_id != Config.CLIENT_ID
        or form_data.client_secret != Config.CLIENT_SECRET
    ):
        return BaseResponse.failed(Error(ErrorCode.INVALID_CLIENT))
