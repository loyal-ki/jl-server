import redis.asyncio
from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordBearer
from loguru import logger
from sqlalchemy.orm import Session

import app.core.exceptions.user.user_exceptions as exceptions
from app.config.config import AppEnv, Config
from app.core.database import get_db
from app.core.entities.user.user_entity import UserEntity
from app.core.redis.redis import get_redis
from app.core.redis.refresh_count_repository import RefreshCountRepository
from app.core.redis.verify_token_repository import VerifyTokenRepository
from app.core.schema.auth.auth_schema import (
    BearerResponse,
    VerifyEmail,
    VerifyPhone,
)
from app.core.schema.base_response import BaseResponse
from app.core.schema.error_schema import Error, ErrorCode
from app.dependencies import get_current_user
from app.infra.email.email_client import (
    EmailClient,
    LoggingEmailClient,
    SESClient,
)
from app.infra.sms.sms_client import LoggingSMSClient, MediaSMSClient, SMSClient
from app.repositories.session.user_session_repository import (
    UserSessionRepository,
)
from app.repositories.session.user_session_repository_protocol import (
    UserSessionRepositoryProtocol,
)
from app.repositories.user.refresh_count_repository import (
    RefreshCountRepositoryProtocol,
)
from app.repositories.user.user_repository import UserRepository
from app.repositories.user.user_repository_protocol import (
    UserRepositoryProtocol,
)
from app.repositories.user.verify_token_repository_protocol import (
    VerifyTokenRepositoryProtocol,
)
from app.usecases.auth.user_verify.user_verify_usecase import (
    UserVerifyInteractor,
    UserVerifyUseCase,
)

router = APIRouter(prefix="/auth/verify", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def user_repository() -> UserRepositoryProtocol:
    return UserRepository()


def verify_user_repository(
    redis: redis.asyncio.Redis = Depends(get_redis),
) -> VerifyTokenRepositoryProtocol:
    return VerifyTokenRepository(redis=redis)


def user_session_repository(
    redis: redis.asyncio.Redis = Depends(get_redis),
) -> UserSessionRepositoryProtocol:
    return UserSessionRepository(redis=redis)


def refresh_count_repository(
    redis: redis.asyncio.Redis = Depends(get_redis),
) -> RefreshCountRepositoryProtocol:
    return RefreshCountRepository(redis=redis)


def email_client() -> EmailClient:
    if Config.APP_ENV == AppEnv.local:
        return LoggingEmailClient()
    return SESClient()


def sms_client() -> SMSClient:
    if Config.APP_ENV == AppEnv.local:
        return LoggingSMSClient()
    return MediaSMSClient()


def user_verify_usecase(
    user_repository: UserRepositoryProtocol = Depends(user_repository),
    verify_token_repository: VerifyTokenRepositoryProtocol = Depends(
        verify_user_repository
    ),
    user_session_repository: UserSessionRepositoryProtocol = Depends(
        user_session_repository
    ),
    refresh_count_repository: RefreshCountRepositoryProtocol = Depends(
        refresh_count_repository
    ),
    session: Session = Depends(get_db),
    email_client: EmailClient = Depends(email_client),
    sms_client: SMSClient = Depends(sms_client),
) -> UserVerifyUseCase:
    return UserVerifyInteractor(
        user_repository=user_repository,
        verify_token_repository=verify_token_repository,
        user_session_repository=user_session_repository,
        refresh_count_repository=refresh_count_repository,
        session=session,
        email_client=email_client,
        sms_client=sms_client,
    )


@router.post(
    "/email",
    summary="Verify Email",
    status_code=status.HTTP_200_OK,
)
async def verify_email(
    data: VerifyEmail,
    user_verify_usecase: UserVerifyUseCase = Depends(user_verify_usecase),
):
    try:
        token = await user_verify_usecase.verify_email(data)

        bearer = BearerResponse(
            access_token=token, token_type="bearer", is_user_verified=True
        )

        return BaseResponse.success(
            BaseResponse.model_to_dict(bearer),
            msg="Verify successfully",
        )

    except exceptions.UserAlreadyVerified:
        return BaseResponse.failed(Error(ErrorCode.ALREADY_VERIFIED))
    except (exceptions.InvalidVerifyToken, exceptions.UserNotExists):
        return BaseResponse.failed(Error(ErrorCode.BAD_TOKEN))
    except Exception:
        logger.exception("error occured while verify user email.")
        return BaseResponse.failed(Error(ErrorCode.INTERNAL_SERVER_ERROR))


@router.post(
    "/email/refresh",
    summary="Refresh email verify token",
    status_code=status.HTTP_200_OK,
)
async def refresh_email_verify_token(
    current_user: UserEntity = Depends(get_current_user),
    user_verify_usecase: UserVerifyUseCase = Depends(user_verify_usecase),
):
    try:
        await user_verify_usecase.refresh_email_verify_token(current_user)
        return BaseResponse.success()

    except exceptions.UserAlreadyVerified:
        return BaseResponse.failed(Error(ErrorCode.ALREADY_VERIFIED))
    except exceptions.RefreshCountLimitExceeded:
        return BaseResponse.failed(Error(ErrorCode.TOO_MANY_REQUESTS))
    except Exception:
        logger.exception("error occured while refreshing verify token.")
        return BaseResponse.failed(Error(ErrorCode.INTERNAL_SERVER_ERROR))


@router.post(
    "/phone",
    summary="User Registration with Phone Number or Authentication After Phone Number Update",
    status_code=status.HTTP_200_OK,
)
async def verify_phone(
    data: VerifyPhone,
    user_verify_usecase: UserVerifyUseCase = Depends(user_verify_usecase),
) -> BearerResponse:
    try:
        token = await user_verify_usecase.verify_phone(data)
        bearer = BearerResponse(
            access_token=token, token_type="bearer", is_user_verified=True
        )

        return BaseResponse.success(
            BaseResponse.model_to_dict(bearer),
            msg="Verify successfully",
        )

    except exceptions.UserAlreadyVerified:
        return BaseResponse.failed(Error(ErrorCode.ALREADY_VERIFIED))
    except (exceptions.InvalidVerifyToken, exceptions.UserNotExists):
        return BaseResponse.failed(Error(ErrorCode.BAD_TOKEN))
    except Exception:
        logger.exception("error occured while verify user.")
        return BaseResponse.failed(Error(ErrorCode.INTERNAL_SERVER_ERROR))


@router.post(
    "/phone/refresh",
    summary="Refresh phone verify token",
    status_code=status.HTTP_200_OK,
)
async def refresh_phone_verify_token(
    current_user: UserEntity = Depends(get_current_user),
    user_verify_usecase: UserVerifyUseCase = Depends(user_verify_usecase),
):
    try:
        await user_verify_usecase.refresh_phone_verify_token(current_user)
        return BaseResponse.success()
    except exceptions.UserAlreadyVerified:
        return BaseResponse.failed(Error(ErrorCode.ALREADY_VERIFIED))

    except exceptions.RefreshCountLimitExceeded:
        return BaseResponse.failed(Error(ErrorCode.TOO_MANY_REQUESTS))

    except Exception:
        logger.exception("error occured while refreshing verify token.")
        return BaseResponse.failed(Error(ErrorCode.INTERNAL_SERVER_ERROR))
