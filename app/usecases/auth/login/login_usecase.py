from typing import Any, Callable, Coroutine, Optional, Protocol, Tuple

from pydantic import SecretStr
from sqlalchemy.orm import Session

import app.core.exceptions.user.user_exceptions as exception
from app.core.entities.user.user_entity import UserEntity
from app.core.schema.auth.auth_schema import (
    UserFacebookLogin,
    UserGoogleLogin,
    UserLogin,
)
from app.core.schema.common_schemas import LoginType
from app.helpers.password import PasswordHelper
from app.repositories.session.user_session_repository_protocol import (
    UserSessionRepositoryProtocol,
)
from app.repositories.user.user_repository_protocol import (
    UserRepositoryProtocol,
)


class LoginUseCase(Protocol):
    async def login(self, credentials: UserLogin) -> Tuple[str, bool]:
        ...  # pragma: no cover

    async def login_facebook(
        self, credentials: UserFacebookLogin
    ) -> Tuple[str, bool]:
        ...  # pragma: no cover

    async def login_google(
        self, credentials: UserGoogleLogin
    ) -> Tuple[str, bool]:
        ...  # pragma: no cover


class LoginInteractor(LoginUseCase):
    def __init__(
        self,
        user_repository: UserRepositoryProtocol,
        user_session_repository: UserSessionRepositoryProtocol,
        session: Session,
    ):
        self.user_repository = user_repository
        self.user_session_repository = user_session_repository
        self.session = session

    async def login(self, credentials: UserLogin) -> tuple[str, bool]:
        # Determine whether it's an email address or a phone number
        # based on whether it's a valid email address or not.
        callable: Callable[
            [Any, str], Coroutine[Any, Any, Optional[UserEntity]]
        ]

        # If credentials. email and credentials.
        # phone are not empty raise exception.
        # UserNotExists exception.
        # UserNotExists
        if not credentials.email and not credentials.phone:
            raise exception.UserNotExists

        login_type = LoginType.PHONE
        # Find a user by email or phone.
        if credentials.email:
            callable = self.user_repository.find_by_email
            login_type = LoginType.EMAIL
            user = await callable(self.session, credentials.email)
        else:
            callable = self.user_repository.find_by_phone
            user = await callable(
                self.session,
                credentials.phone.get_secret_value()
                if isinstance(credentials.phone, SecretStr)
                else credentials.phone,
            )

        # If user is not logged in raise exception. UserNotExists
        if not user:
            # Timing attack prevention https://code.djangoproject.com/ticket/20760
            PasswordHelper().hash(credentials.password)
            raise exception.UserNotExists

        verified = PasswordHelper().verify(
            plain_password=credentials.password,
            hashed_password=user.hashed_password,
        )
        # Verify that the password is valid.
        if not verified:
            raise exception.InvalidPassword

        # Raises exception. UserDeleted if user has been deleted.
        if user.deleted_at:
            raise exception.UserDeleted

        is_user_verified: bool = False
        # Check if the user is verified.
        if (login_type == LoginType.EMAIL and user.is_email_verified) or (
            login_type == LoginType.PHONE and user.is_phone_verified
        ):
            is_user_verified = True

        token: str = await self.user_session_repository.write_token(
            user, login_type
        )

        return token, is_user_verified

    async def login_facebook(
        self, credentials: UserFacebookLogin
    ) -> tuple[str, bool]:
        # validate
        if not credentials.facebook_id:
            raise exception.RequiredFacebookId
        if not credentials.facebook_access_token:
            raise exception.RequiredFacebookAccessToken

        callable: Callable[
            [Any, str], Coroutine[Any, Any, Optional[UserEntity]]
        ]

        callable = self.user_repository.find_by_facebook_id

        user = await callable(self.session, credentials.facebook_id)

        if not user:
            # Timing attack prevention https://code.djangoproject.com/ticket/20760
            raise exception.UserNotExists

        is_user_verified: bool = False

        # Check if the user is verified.
        if user and user.is_facebook_verified:
            is_user_verified = True

        token: str = await self.user_session_repository.write_token(
            user, LoginType.FACEBOOK
        )

        return token, is_user_verified

    async def login_google(
        self, credentials: UserGoogleLogin
    ) -> tuple[str, bool]:
        # validate
        if not credentials.google_id:
            raise exception.RequiredFacebookId
        if not credentials.google_access_token:
            raise exception.RequiredFacebookAccessToken

        callable: Callable[
            [Any, str], Coroutine[Any, Any, Optional[UserEntity]]
        ]

        callable = self.user_repository.find_by_google_id

        user = await callable(self.session, credentials.google_id)

        if not user:
            # Timing attack prevention https://code.djangoproject.com/ticket/20760
            raise exception.UserNotExists

        is_user_verified: bool = False

        # Check if the user is verified.
        if user and user.is_google_verified:
            is_user_verified = True

        token: str = await self.user_session_repository.write_token(
            user, LoginType.GOOGLE
        )

        return token, is_user_verified
