from typing import Protocol

from sqlalchemy.orm import Session

import app.core.exceptions.user.user_exceptions as exception
from app.config.config import Config
from app.helpers import jwt
from app.repositories.session.user_session_repository_protocol import (
    UserSessionRepositoryProtocol,
)
from app.repositories.user.user_repository_protocol import (
    UserRepositoryProtocol,
)


class CheckVerificationUseCase(Protocol):
    async def check_verification(self, token: str) -> bool:
        ...  # pragma: no cover


class CheckVerificationInteractor(CheckVerificationUseCase):
    def __init__(
        self,
        user_repository: UserRepositoryProtocol,
        user_session_repository: UserSessionRepositoryProtocol,
        session: Session,
    ):
        self.user_repository = user_repository
        self.user_session_repository = user_session_repository
        self.session = session

    async def check_verification(self, token: str) -> bool:
        user_id = await self.user_session_repository.read_token(token)
        # Raise exception. InvalidToken if user_id is not a valid token.
        if not user_id:
            raise exception.InvalidToken
        try:
            user = await self.user_repository.find_by_id(self.session, user_id)
            payload = jwt.decode_jwt(token, Config.JWT_TOKEN_SECRET)
            user_email_or_phone = payload.get("email")
            # Returns true if the user is email or phone.
            if not user_email_or_phone:
                user_email_or_phone = payload.get("phone")
                # Return True if the user is a phone number verified False otherwise.
                if not user.is_phone_verified:
                    return False
            else:
                # Return True if the user is not verified.
                if not user.is_email_verified:
                    return False
        except Exception:
            return False
        return True
