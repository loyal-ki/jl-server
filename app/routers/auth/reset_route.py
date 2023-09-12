import redis.asyncio
from fastapi import APIRouter, Depends, status
from loguru import logger
from sqlalchemy.orm import Session

import app.core.exceptions.user.user_exceptions as exception
from app.config.config import AppEnv, Config
from app.core.database import get_db
from app.core.redis.redis import get_redis
from app.core.redis.reset_repository import ResetRepository
from app.core.schema.auth.auth_schema import (
    ForgotPasswordEmail,
    ForgotPasswordPhone,
    ResetPassword,
)
from app.core.schema.base_response import BaseResponse
from app.core.schema.error_schema import Error, ErrorCode
from app.dependencies import check_client_credential
from app.infra.email.email_client import (
    EmailClient,
    LoggingEmailClient,
    SESClient,
)
from app.infra.sms.sms_client import LoggingSMSClient, MediaSMSClient, SMSClient
from app.repositories.user.reset_repository import ResetRepositoryProtocol
from app.repositories.user.user_repository import UserRepository
from app.repositories.user.user_repository_protocol import (
    UserRepositoryProtocol,
)
from app.usecases.auth.reset.reset_usecase import ResetInteractor, ResetUseCase

router = APIRouter(prefix="/auth", tags=["auth"])


def user_repository() -> UserRepositoryProtocol:
    return UserRepository()


def reset_repository(
    redis: redis.asyncio.Redis = Depends(get_redis),
) -> ResetRepositoryProtocol:
    return ResetRepository(redis=redis)


def email_client() -> EmailClient:
    if Config.APP_ENV == AppEnv.local:
        return LoggingEmailClient()
    return SESClient()


def sms_client() -> SMSClient:
    if Config.APP_ENV == AppEnv.local:
        return LoggingSMSClient()
    return MediaSMSClient()


def reset_usecase(
    session: Session = Depends(get_db),
    user_repository: UserRepositoryProtocol = Depends(user_repository),
    reset_repository: ResetRepositoryProtocol = Depends(reset_repository),
    email_client: EmailClient = Depends(email_client),
    sms_client: SMSClient = Depends(sms_client),
) -> ResetUseCase:
    return ResetInteractor(
        user_repository=user_repository,
        session=session,
        reset_repository=reset_repository,
        email_client=email_client,
        sms_client=sms_client,
    )


@router.post(
    "/forgot-password/email",
    summary="Sending Email for Password Reset",
    status_code=status.HTTP_200_OK,
)
async def forgot_password_by_email(
    form_data: ForgotPasswordEmail,
    reset_usecase: ResetUseCase = Depends(reset_usecase),
):
    check_client_credential(form_data)
    try:
        await reset_usecase.reset_by_email(form_data)
        return BaseResponse.success()
    except exception.UserNotExists:
        return BaseResponse.failed(Error(ErrorCode.USER_NOT_EXISTS))

    except Exception:
        logger.exception("Error happened when resetting password by email.")
        return BaseResponse.failed(Error(ErrorCode.INTERNAL_SERVER_ERROR))


@router.post(
    "/forgot-password/phone",
    summary="Sending SMS for Password Reset",
    status_code=status.HTTP_200_OK,
)
async def forgot_password_by_phone(
    form_data: ForgotPasswordPhone,
    reset_usecase: ResetUseCase = Depends(reset_usecase),
):
    check_client_credential(form_data)
    try:
        await reset_usecase.reset_by_phone(form_data)
        return BaseResponse.success()
    except exception.UserNotExists:
        return BaseResponse.failed(Error(ErrorCode.USER_NOT_EXISTS))

    except Exception:
        logger.exception("Error happened when resetting password by phone.")
        return BaseResponse.failed(Error(ErrorCode.INTERNAL_SERVER_ERROR))


@router.post(
    "/reset-password",
    summary="Reset-password",
    status_code=status.HTTP_200_OK,
)
async def reset_password(
    data: ResetPassword, reset_usecase: ResetUseCase = Depends(reset_usecase)
):
    try:
        await reset_usecase.reset(data)
        return BaseResponse.success()
    except exception.UserNotExists:
        return BaseResponse.failed(Error(ErrorCode.USER_NOT_EXISTS))

    except exception.InvalidResetToken:
        return BaseResponse.failed(Error(ErrorCode.BAD_TOKEN))

    except Exception:
        logger.exception("Error happened when resetting password.")
        return BaseResponse.failed(Error(ErrorCode.INTERNAL_SERVER_ERROR))
