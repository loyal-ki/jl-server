from typing import Protocol

from loguru import logger
from sqlalchemy.orm import Session

import app.core.exceptions.user.user_exceptions as exception
from app.config.config import Config
from app.core.entities.user.sex_entity import SexEntity
from app.core.entities.user.user_entity import UserEntity
from app.core.schema.user.user_schema import (
    UserEmailCreate,
    UserFacebookCreate,
    UserGoogleCreate,
    UserPhoneCreate,
    UserRead,
)
from app.helpers.password import PasswordHelper
from app.infra.email.email_client import EmailClient
from app.infra.facebook.facebook_client import FacebookClient
from app.infra.google.google_client import GoogleClient
from app.infra.sms.sms_client import SMSClient
from app.message_template import MessageTemplate
from app.repositories.user.user_repository_protocol import (
    UserRepositoryProtocol,
)
from app.repositories.user.verify_token_repository_protocol import (
    VerifyTokenRepositoryProtocol,
)


class UserRegisterUseCase(Protocol):
    async def create_by_email(
        self, user_email_create: UserEmailCreate
    ) -> UserRead:
        ...  # pragma: no cover

    async def create_by_phone(
        self, user_phone_create: UserPhoneCreate
    ) -> UserRead:
        ...  # pragma: no cover

    async def create_by_facebook(
        self, user_facebook_create: UserFacebookCreate
    ) -> UserRead:
        ...  # pragma: no cover

    async def create_by_google(
        self, user_google_create: UserGoogleCreate
    ) -> UserRead:
        ...  # pragma: no cover


class UserRegisterInteractor(UserRegisterUseCase):
    def __init__(
        self,
        session: Session,
        user_repository: UserRepositoryProtocol,
        verify_token_repository: VerifyTokenRepositoryProtocol,
        email_client: EmailClient,
        sms_client: SMSClient,
        facebook_client: FacebookClient,
        google_client: GoogleClient,
    ):
        self.session = session
        self.user_repository = user_repository
        self.verify_token_repository = verify_token_repository
        self.email_client = email_client
        self.sms_client = sms_client
        self.facebook_client = facebook_client
        self.google_client = google_client

    async def create_by_email(
        self, user_email_create: UserEmailCreate
    ) -> UserRead:
        user = await self.user_repository.find_by_email(
            self.session, user_email_create.email
        )
        # If the user is a valid email address.
        if user:
            if not user.is_email_verified:
                raise exception.EmailHasNotBeenVerified
            raise exception.EmailAlreadyExists

        hashed_password = PasswordHelper().hash(user_email_create.password)
        try:
            self.session.begin()
            # Update the user s hashed_password.
            if user:
                user.hashed_password = hashed_password
                try:
                    user = await self.user_repository.update(self.session, user)
                except exception.UserNotExists:
                    user = None
            # Create or update a user.
            if not user:
                user = UserEntity(
                    email=user_email_create.email,
                    hashed_password=hashed_password,
                    sex_code=SexEntity.CODE_NOT_KNOWN,
                    is_email_verified=False,
                    is_phone_verified=False,
                    is_facebook_verified=False,
                    is_google_verified=False,
                )
                user = await self.user_repository.create(self.session, user)
                user.generate_user_code_if_empty()
                user = await self.user_repository.update(self.session, user)

            token = await self.verify_token_repository.write_email_token(user)
            self.email_client.send_email(
                sender=Config.MAIL_SENDER,
                to=[user_email_create.email],
                reply_to=[Config.MAIL_REPLY_TO],
                subject="[Journey Lingua App] Provisional Registration Complete / Request for Main Registration Procedures",  # noqa: E501
                text=MessageTemplate.verify_email_text(token),
            )
            await self.session.commit()
        except Exception as e:
            logger.exception("user creation by email failed.")
            await self.session.rollback()
            raise e
        return UserRead.from_entity(user)

    async def create_by_phone(
        self, user_phone_create: UserPhoneCreate
    ) -> UserRead:
        user = await self.user_repository.find_by_phone(
            self.session, str(user_phone_create.phone)
        )
        # If the user is a phone.
        if user:
            if not user.is_phone_verified:
                raise exception.PhoneHasNotBeenVerified
            raise exception.PhoneAlreadyExists

        hashed_password = PasswordHelper().hash(user_phone_create.password)
        try:
            self.session.begin()
            # Update the user s hashed_password.
            if user:
                user.hashed_password = hashed_password
                try:
                    user = await self.user_repository.update(self.session, user)
                except exception.UserNotExists:
                    user = None
            # Create or update a user.
            if not user:
                user = UserEntity(
                    phone=str(user_phone_create.phone),
                    hashed_password=hashed_password,
                    sex_code=SexEntity.CODE_NOT_KNOWN,
                    is_email_verified=False,
                    is_phone_verified=False,
                    is_facebook_verified=False,
                    is_google_verified=False,
                )
                user = await self.user_repository.create(self.session, user)
                user.generate_user_code_if_empty()
                user = await self.user_repository.update(self.session, user)
            pin = await self.verify_token_repository.write_phone_pin_code(user)
            self.sms_client.send_sms(
                user_phone_create.phone, MessageTemplate.verify_sms_text(pin)
            )
            await self.session.commit()
        except Exception as e:
            logger.exception("user creation by phone failed.")
            await self.session.rollback()
            raise e
        return UserRead.from_entity(user)

    async def create_by_facebook(
        self, user_facebook_create: UserFacebookCreate
    ) -> UserRead:
        user = await self.user_repository.find_by_facebook_id(
            self.session, str(user_facebook_create.facebook_id)
        )

        if user:
            raise exception.FacebookAccountAlreadyExists

        try:
            self.session.begin()
            # Create or update a user.
            if not user:
                is_facebook_verified = (
                    await self.facebook_client.is_valid_access_token(
                        user_facebook_create.facebook_id,
                        user_facebook_create.facebook_access_token,
                    )
                )

                logger.info(is_facebook_verified)

                if not is_facebook_verified:
                    raise exception.InvalidFacebookIdOrToken

                logger.info(f"is_facebook_verified: {is_facebook_verified}")

                user = UserEntity(
                    facebook_id=str(user_facebook_create.facebook_id),
                    facebook_access_token=user_facebook_create.facebook_access_token,
                    sex_code=SexEntity.CODE_NOT_KNOWN,
                    hashed_password="",
                    is_email_verified=False,
                    is_phone_verified=False,
                    is_facebook_verified=is_facebook_verified,
                    is_google_verified=False,
                )

                user = await self.user_repository.create(self.session, user)
                user.generate_user_code_if_empty()
                user = await self.user_repository.update(self.session, user)
            await self.session.commit()
        except Exception as e:
            logger.exception("user creation by google failed.")
            await self.session.rollback()
            raise e
        return UserRead.from_entity(user)

    async def create_by_google(
        self, user_google_create: UserGoogleCreate
    ) -> UserRead:
        user = await self.user_repository.find_by_google_id(
            self.session, str(user_google_create.google_id)
        )

        if user:
            raise exception.GoogleAccountAlreadyExists

        try:
            self.session.begin()
            # Create or update a user.
            if not user:
                is_google_verified = (
                    await self.google_client.is_valid_access_token(
                        user_google_create.google_id,
                        user_google_create.google_access_token,
                    )
                )

                if not is_google_verified:
                    raise exception.InvalidGoogleIdOrToken

                user = UserEntity(
                    facebook_id=str(user_google_create.google_id),
                    facebook_access_token=user_google_create.google_access_token,
                    sex_code=SexEntity.CODE_NOT_KNOWN,
                    hashed_password="",
                    is_email_verified=False,
                    is_phone_verified=False,
                    is_facebook_verified=False,
                    is_google_verified=is_google_verified,
                )

                user = await self.user_repository.create(self.session, user)
                user.generate_user_code_if_empty()
                user = await self.user_repository.update(self.session, user)
            await self.session.commit()
        except Exception as e:
            logger.exception("user creation by google failed.")
            await self.session.rollback()
            raise e
        return UserRead.from_entity(user)
