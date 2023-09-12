import redis.asyncio
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

import app.core.exceptions.user.user_exceptions as exception
from app.config.config import AppEnv, Config
from app.core.database import get_db
from app.core.redis.redis import get_redis
from app.core.redis.verify_token_repository import VerifyTokenRepository
from app.core.schema.auth.auth_schema import BearerResponse, UserLogin
from app.core.schema.base_response import BaseResponse
from app.core.schema.common_schemas import LoginType
from app.core.schema.error_schema import Error, ErrorCode
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
from app.repositories.session.user_session_repository import (
    UserSessionRepository,
)
from app.repositories.session.user_session_repository_protocol import (
    UserSessionRepositoryProtocol,
)
from app.repositories.user.user_repository import UserRepository
from app.repositories.user.user_repository_protocol import (
    UserRepositoryProtocol,
)
from app.repositories.user.verify_token_repository_protocol import (
    VerifyTokenRepositoryProtocol,
)
from app.usecases.auth.login.login_usecase import LoginInteractor, LoginUseCase
from app.usecases.auth.register.register_usecase import (
    UserRegisterInteractor,
    UserRegisterUseCase,
)
from app.utils.logger import Log

log = Log("Auth Route")

router = APIRouter(prefix="/auth", tags=["auth"])


def user_repository() -> UserRepositoryProtocol:
    return UserRepository()


def user_session_repository(
    redis: redis.asyncio.Redis = Depends(get_redis),
) -> UserSessionRepositoryProtocol:
    return UserSessionRepository(redis=redis)


def login_usecase(
    user_repository: UserRepositoryProtocol = Depends(user_repository),
    user_session_repository: UserSessionRepositoryProtocol = Depends(
        user_session_repository
    ),
    session: Session = Depends(get_db),
) -> LoginUseCase:
    return LoginInteractor(
        user_repository=user_repository,
        user_session_repository=user_session_repository,
        session=session,
    )


def google_client() -> GoogleClientProtocol:
    return GoogleClient()


def facebook_client() -> FacebookClientProtocol:
    return FacebookClient()


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
    "/login",
    summary="Login",
    status_code=status.HTTP_200_OK,
)
async def login(
    form_data: UserLogin,
    login_usecase: LoginUseCase = Depends(login_usecase),
):
    """
    Handle the login request.

    Args:
        form_data (UserLogin): The user login data.
        login_usecase (LoginUseCase, optional): The login use case. Defaults to Depends(login_usecase).

    Returns:
        Response: The login response.
    """
    # Check client credentials
    check_client_credential(form_data)

    try:
        # Perform the login and get the token and user verification status
        if (
            form_data.login_type is LoginType.EMAIL
            or form_data.login_type is LoginType.PHONE
        ):
            token, is_user_verified = await login_usecase.login(
                credentials=form_data
            )
        if form_data.login_type is LoginType.FACEBOOK:
            token, is_user_verified = await login_usecase.login_facebook(
                credentials=form_data
            )
        if form_data.login_type is LoginType.GOOGLE:
            token, is_user_verified = await login_usecase.login_google(
                credentials=form_data
            )

        # Create the bearer response
        bearer = BearerResponse(
            access_token=token,
            token_type="bearer",
            is_user_verified=is_user_verified,
        )

        # Return the success response
        return BaseResponse.success(
            BaseResponse.model_to_dict(bearer),
            msg="Login successfully",
        )

    except exception.InvalidFacebookIdOrToken:
        return BaseResponse.failed(
            Error(ErrorCode.INVALID_FACEBOOK_ID_OR_TOKEN)
        )

    except exception.RequiredFacebookId:
        return BaseResponse.failed(Error(ErrorCode.REQUIRED_FACEBOOK_ID))

    except exception.RequiredFacebookAccessToken:
        return BaseResponse.failed(
            Error(ErrorCode.REQUIRED_FACEBOOK_ACCESS_TOKEN)
        )

    except exception.InvalidGoogleIdOrToken:
        return BaseResponse.failed(Error(ErrorCode.INVALID_GOOGLE_ID_OR_TOKEN))

    except exception.RequiredGoogleId:
        return BaseResponse.failed(Error(ErrorCode.REQUIRED_GOOGLE_ID))

    except exception.RequiredGoogleAccessToken:
        return BaseResponse.failed(
            Error(ErrorCode.REQUIRED_GOOGLE_ACCESS_TOKEN)
        )

    except exception.UserNotExists:
        return BaseResponse.failed(Error(ErrorCode.USER_NOT_EXISTS))

    except exception.InvalidPassword:
        return BaseResponse.failed(Error(ErrorCode.INVALID_PASSWORD))

    except exception.UserDeleted:
        return BaseResponse.failed(Error(ErrorCode.USER_DELETED))

    except Exception:
        return BaseResponse.failed(Error(ErrorCode.INTERNAL_SERVER_ERROR))
