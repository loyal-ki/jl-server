from typing import Optional, Protocol

from loguru import logger
from sqlalchemy.orm import Session

import app.core.exceptions.user.user_exceptions as exception
from app.config.config import Config
from app.core.entities.user.user_entity import UserEntity
from app.core.schema.auth.auth_schema import VerifyEmail, VerifyPhone
from app.core.schema.common_schemas import LoginType
from app.infra.email.email_client import EmailClient
from app.infra.sms.sms_client import SMSClient
from app.message_template import MessageTemplate
from app.repositories.session.user_session_repository_protocol import (
    UserSessionRepositoryProtocol,
)
from app.repositories.user.refresh_count_repository import (
    RefreshCountRepositoryProtocol,
)
from app.repositories.user.user_repository_protocol import (
    UserRepositoryProtocol,
)
from app.repositories.user.verify_token_repository_protocol import (
    VerifyTokenRepositoryProtocol,
)


class UserVerifyUseCase(Protocol):
    async def verify_email(self, verify_email: VerifyEmail) -> str:
        ...  # pragma: no cover

    async def verify_phone(self, verify_phone: VerifyPhone) -> str:
        ...  # pragma: no cover

    async def refresh_email_verify_token(self, user: UserEntity) -> None:
        ...  # pragma: no cover

    async def refresh_phone_verify_token(self, user: UserEntity) -> None:
        ...  # pragma: no cover


class UserVerifyInteractor(UserVerifyUseCase):
    def __init__(
        self,
        user_repository: UserRepositoryProtocol,
        verify_token_repository: VerifyTokenRepositoryProtocol,
        user_session_repository: UserSessionRepositoryProtocol,
        refresh_count_repository: RefreshCountRepositoryProtocol,
        session: Session,
        email_client: EmailClient,
        sms_client: SMSClient,
    ):
        self.user_repository = user_repository
        self.verify_token_repository = verify_token_repository
        self.user_session_repository = user_session_repository
        self.refresh_count_repository = refresh_count_repository
        self.session = session
        self.email_client = email_client
        self.sms_client = sms_client

    async def verify_email(self, verify_email: VerifyEmail) -> str:
        email = await self.verify_token_repository.read_token(
            verify_email.token
        )
        # Verify token is not valid.
        if not email:
            raise exception.InvalidVerifyToken()

        user: Optional[UserEntity] = await self.user_repository.find_by_email(
            self.session, email
        )
        # If user is not logged in raise exception. UserNotExists
        if not user:
            raise exception.UserNotExists()
        # If the user is already verified raise an exception.
        # UserAlreadyVerified exception.
        if user.is_email_verified:
            raise exception.UserAlreadyVerified()

        user.is_email_verified = True
        user = await self.user_repository.update(self.session, user)
        try:
            await self.verify_token_repository.destroy_token(verify_email.token)
        except Exception as e:
            # Skipping even if the token deletion fails as
            # it won't impact the user
            logger.warning(f"Failed to destroy token: {e}")
        try:
            await self.refresh_count_repository.destroy_count(user)
        except Exception as e:
            # Skipping as user won't be affected even if count deletion fails
            logger.warning(f"Failed to destroy count: {e}")
        return await self.user_session_repository.write_token(
            user, LoginType.EMAIL
        )

    async def verify_phone(self, verify_phone: VerifyPhone) -> str:
        phone = await self.verify_token_repository.read_token(verify_phone.pin)
        # Verify token is not a valid phone number.
        if not phone:
            raise exception.InvalidVerifyToken()

        user: Optional[UserEntity] = await self.user_repository.find_by_phone(
            session=self.session, phone=phone
        )
        # If user is not logged in raise exception. UserNotExists
        if not user:
            raise exception.UserNotExists()
        # If the user is not a phone number.
        if user.is_phone_verified:
            raise exception.UserAlreadyVerified()

        user.is_phone_verified = True
        user = await self.user_repository.update(
            session=self.session, user=user
        )
        try:
            await self.verify_token_repository.destroy_token(verify_phone.pin)
        except Exception as e:
            # Skipping even if the token deletion fails as
            # it won't impact the user
            logger.warning(f"Failed to destroy token: {e}")
        try:
            await self.refresh_count_repository.destroy_count(user)
        except Exception as e:
            # Skipping as user won't be affected even if count deletion fails
            logger.warning(f"Failed to destroy count: {e}")
        return await self.user_session_repository.write_token(
            user, LoginType.PHONE
        )

    async def refresh_email_verify_token(self, user: UserEntity):
        try:
            self.session.begin()
            # If the user is already verified raise exception.
            # UserAlreadyVerified exception.
            # UserAlreadyVerified exception.
            if user.is_email_verified:
                raise exception.UserAlreadyVerified

            count = await self.refresh_count_repository.read_count(user)
            # If the count exceeds the limit of the refresh count
            # limit raise an exception.
            if count >= Config.REFRESH_COUNT_LIMIT:
                raise exception.RefreshCountLimitExceeded

            token = await self.verify_token_repository.write_email_token(user)
            await self.refresh_count_repository.write_count(
                user_entity=user, count=count + 1
            )

            self.email_client.send_email(
                sender=Config.MAIL_SENDER,
                to=[user.email],
                reply_to=[Config.MAIL_REPLY_TO],
                subject="[Journey Lingua App] Pre-registration Completed / Request for Final Registration Process",  # noqa: E501
                text=MessageTemplate.verify_email_text(token),
            )
            await self.session.commit()
        except Exception as e:
            logger.exception("refresh email verify token failed.")
            await self.session.rollback()
            raise e

    async def refresh_phone_verify_token(self, user: UserEntity):
        try:
            self.session.begin()
            # If the user is already verified raise exception.
            # UserAlreadyVerified exception.
            # UserAlreadyVerified exception.
            if user.is_email_verified:
                raise exception.UserAlreadyVerified

            count = await self.refresh_count_repository.read_count(user)
            # If the count exceeds the limit of the refresh count
            # limit raise an exception. RefreshCountLimitExceeded exception.
            if count >= Config.REFRESH_COUNT_LIMIT:
                raise exception.RefreshCountLimitExceeded
            pin = await self.verify_token_repository.write_phone_pin_code(user)
            await self.refresh_count_repository.write_count(
                user_entity=user, count=count + 1
            )
            self.sms_client.send_sms(
                user.phone, MessageTemplate.verify_sms_text(pin)
            )
            await self.session.commit()
        except Exception as e:
            logger.exception("Refresh phone verify token failed.")
            await self.session.rollback()
            raise e
