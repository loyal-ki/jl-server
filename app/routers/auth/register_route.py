import redis.asyncio
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

import app.core.exceptions.user.user_exceptions as exception
from app.config.config import AppEnv, Config
from app.core.database import get_db
from app.core.redis.redis import get_redis
from app.core.redis.verify_token_repository import VerifyTokenRepository
from app.core.schema.base_response import BaseResponse
from app.core.schema.error_schema import Error, ErrorCode
from app.core.schema.user.user_schema import (
    UserEmailCreate,
    UserFacebookCreate,
    UserGoogleCreate,
    UserPhoneCreate,
)
from app.dependencies import check_client_credential
from app.infra.email.email_client import (
    EmailClient,
    LoggingEmailClient,
    SESClient,
)
from app.infra.facebook.facebook_client import (
    FacebookClient,
    FacebookClientProtocol,
)
from app.infra.google.google_client import GoogleClient, GoogleClientProtocol
from app.infra.sms.sms_client import LoggingSMSClient, MediaSMSClient, SMSClient
from app.repositories.user.user_repository import UserRepository
from app.repositories.user.user_repository_protocol import (
    UserRepositoryProtocol,
)
from app.repositories.user.verify_token_repository_protocol import (
    VerifyTokenRepositoryProtocol,
)
from app.usecases.auth.register.register_usecase import (
    UserRegisterInteractor,
    UserRegisterUseCase,
)
from app.utils.logger import Log

log = Log("Register Route")

router = APIRouter(prefix="/auth", tags=["auth"])


def user_repository() -> UserRepositoryProtocol:
    return UserRepository()


def verify_token_repository(
    redis: redis.asyncio.Redis = Depends(get_redis),
) -> VerifyTokenRepositoryProtocol:
    return VerifyTokenRepository(redis=redis)


def email_client() -> EmailClient:
    if Config.APP_ENV == AppEnv.local:
        return LoggingEmailClient()
    return SESClient()


def sms_client() -> SMSClient:
    if Config.APP_ENV == AppEnv.local:
        return LoggingSMSClient()
    return MediaSMSClient()


def google_client() -> GoogleClientProtocol:
    return GoogleClient()


def facebook_client() -> FacebookClientProtocol:
    return FacebookClient()


def user_create_usecase(
    session: Session = Depends(get_db),
    user_repository: UserRepositoryProtocol = Depends(user_repository),
    verify_token_repository: VerifyTokenRepositoryProtocol = Depends(
        verify_token_repository
    ),
    email_client: EmailClient = Depends(email_client),
    sms_client: SMSClient = Depends(sms_client),
    facebook_client: FacebookClient = Depends(facebook_client),
    google_client: GoogleClient = Depends(google_client),
) -> UserRegisterUseCase:
    return UserRegisterInteractor(
        user_repository=user_repository,
        session=session,
        verify_token_repository=verify_token_repository,
        email_client=email_client,
        sms_client=sms_client,
        facebook_client=facebook_client,
        google_client=google_client,
    )


@router.post(
    "/email",
    summary="User registration with phone mail",
    status_code=status.HTTP_200_OK,
)
async def register_by_email(
    form_data: UserEmailCreate,
    user_create_usecase: UserRegisterUseCase = Depends(user_create_usecase),
):
    check_client_credential(form_data)
    try:
        log.exception("Start to user registration.")
        await user_create_usecase.create_by_email(form_data)
        return BaseResponse.success()

    except exception.EmailHasNotBeenVerified:
        return BaseResponse.failed(Error(ErrorCode.NOT_VERIFIED))

    except exception.EmailAlreadyExists:
        return BaseResponse.failed(Error(ErrorCode.EMAIL_ALREADY_EXISTS))

    except Exception:
        log.exception("error occured while creating a user.")
        return BaseResponse.failed(Error(ErrorCode.INTERNAL_SERVER_ERROR))


@router.post(
    "/phone",
    summary="User registration with phone number",
    status_code=status.HTTP_200_OK,
)
async def register_by_phone(
    form_data: UserPhoneCreate,
    user_create_usecase: UserRegisterUseCase = Depends(user_create_usecase),
):
    check_client_credential(form_data)
    try:
        await user_create_usecase.create_by_phone(form_data)
        return BaseResponse.success()

    except exception.PhoneHasNotBeenVerified:
        return BaseResponse.failed(Error(ErrorCode.NOT_VERIFIED))

    except exception.PhoneAlreadyExists:
        return BaseResponse.failed(Error(ErrorCode.PHONE_ALREADY_EXISTS))

    except Exception:
        log.exception("Error occured while creating a user.")
        return BaseResponse.failed(Error(ErrorCode.INTERNAL_SERVER_ERROR))


@router.post(
    "/facebook",
    summary="User registration with facebook",
    status_code=status.HTTP_200_OK,
)
async def register_by_facebook(
    form_data: UserFacebookCreate,
    user_create_usecase: UserRegisterUseCase = Depends(user_create_usecase),
):
    check_client_credential(form_data)
    try:
        await user_create_usecase.create_by_facebook(form_data)
        return BaseResponse.success()

    except exception.FacebookAccountAlreadyExists:
        return BaseResponse.failed(
            Error(ErrorCode.ALREADY_EXISTS_FACEBOOK_ACCOUNT)
        )

    except exception.InvalidFacebookIdOrToken:
        return BaseResponse.failed(
            Error(ErrorCode.INVALID_FACEBOOK_ID_OR_TOKEN)
        )

    except Exception:
        log.exception("Error occured while creating a user.")
        return BaseResponse.failed(Error(ErrorCode.INTERNAL_SERVER_ERROR))


@router.post(
    "/google",
    summary="User registration with google",
    status_code=status.HTTP_200_OK,
)
async def register_by_google(
    form_data: UserGoogleCreate,
    user_create_usecase: UserRegisterUseCase = Depends(user_create_usecase),
):
    check_client_credential(form_data)
    try:
        await user_create_usecase.create_by_google(form_data)
        return BaseResponse.success()

    except exception.GoogleAccountAlreadyExists:
        return BaseResponse.failed(
            Error(ErrorCode.ALREADY_EXISTS_GOOGLE_ACCOUNT)
        )

    except exception.InvalidGoogleAccessToken:
        return BaseResponse.failed(Error(ErrorCode.INVALID_GOOGLE_ID_OR_TOKEN))

    except exception.InvalidGoogleIdOrToken:
        return BaseResponse.failed(Error(ErrorCode.INVALID_GOOGLE_ID_OR_TOKEN))

    except Exception:
        log.exception("Error occured while creating a user.")
        return BaseResponse.failed(Error(ErrorCode.INTERNAL_SERVER_ERROR))
