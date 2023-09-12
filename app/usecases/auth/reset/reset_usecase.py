from typing import Protocol

from loguru import logger
from sqlalchemy.orm import Session

import app.core.exceptions.user.user_exceptions as exception
from app.config.config import Config
from app.core.schema.auth.auth_schema import (
    ForgotPasswordEmail,
    ForgotPasswordPhone,
    ResetPassword,
)
from app.helpers.password import PasswordHelper
from app.infra.email.email_client import EmailClient
from app.infra.sms.sms_client import SMSClient
from app.message_template import MessageTemplate
from app.repositories.user.reset_repository import ResetRepositoryProtocol
from app.repositories.user.user_repository_protocol import (
    UserRepositoryProtocol,
)


class ResetUseCase(Protocol):
    async def reset_by_email(self, forgot_by_email: ForgotPasswordEmail):
        ...  # pragma: no cover

    async def reset_by_phone(self, forgot_by_phone: ForgotPasswordPhone):
        ...  # pragma: no cover

    async def reset(self, reset_info: ResetPassword):
        ...  # pragma: no cover


class ResetInteractor(ResetUseCase):
    def __init__(
        self,
        session: Session,
        user_repository: UserRepositoryProtocol,
        reset_repository: ResetRepositoryProtocol,
        email_client: EmailClient,
        sms_client: SMSClient,
    ):
        self.session = session
        self.user_repository = user_repository
        self.reset_repository = reset_repository
        self.email_client = email_client
        self.sms_client = sms_client

    async def reset_by_email(self, forgot_by_email: ForgotPasswordEmail):
        user = await self.user_repository.find_by_email(
            self.session, forgot_by_email.email
        )
        # If user is not logged in raise exception. UserNotExists
        if not user:
            raise exception.UserNotExists
        try:
            token = await self.reset_repository.write_token(str(user.id))
            self.email_client.send_email(
                sender=Config.MAIL_SENDER,
                to=[user.email],
                reply_to=[Config.MAIL_REPLY_TO],
                subject="[journey Lingua App]Request for Password Reset Procedure",  # noqa: E501
                text=MessageTemplate.reset_email_text(token),
            )
        except Exception as e:
            logger.exception(e)
            raise e

    async def reset_by_phone(self, forgot_by_phone: ForgotPasswordPhone):
        user = await self.user_repository.find_by_phone(
            self.session, forgot_by_phone.phone
        )
        # If user is not logged in raise exception. UserNotExists
        if not user:
            raise exception.UserNotExists
        try:
            token = await self.reset_repository.write_token(str(user.id))
            self.sms_client.send_sms(
                user.phone, MessageTemplate.reset_sms_text(token)
            )
        except Exception as e:
            logger.exception(e)
            raise e

    async def reset(self, reset_info: ResetPassword):
        user_id = await self.reset_repository.read_token(reset_info.token)
        # Raise an exception. InvalidResetToken if the reset token is invalid.
        if not user_id:
            raise exception.InvalidResetToken()

        user = await self.user_repository.find_by_id(self.session, user_id)
        # If user is not logged in raise exception. UserNotExists
        if not user:
            raise exception.UserNotExists()

        hashed_password = PasswordHelper().hash(
            reset_info.password.get_secret_value()
        )
        user.hashed_password = hashed_password
        await self.user_repository.update(self.session, user)
        await self.reset_repository.destroy_token(reset_info.token)
