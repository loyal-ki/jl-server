from typing import Optional, Protocol

from sqlalchemy.orm import Session

from app.config.config import Config
from app.core.entities.user.user_entity import UserEntity
from app.helpers import jwt
from app.repositories.session.user_session_repository_protocol import (
    UserSessionRepositoryProtocol,
)
from app.repositories.user.user_repository_protocol import (
    UserRepositoryProtocol,
)


class GetCurrentUserUseCase(Protocol):
    async def get_current_user(self, token: str) -> Optional[UserEntity]:
        ...  # pragma: no cover


class GetCurrentUserInteractor(GetCurrentUserUseCase):
    def __init__(
        self,
        user_repository: UserRepositoryProtocol,
        user_session_repository: UserSessionRepositoryProtocol,
        session: Session,
    ):
        self.user_repository = user_repository
        self.user_session_repository = user_session_repository
        self.session = session

    async def get_current_user(self, token: str) -> Optional[UserEntity]:
        user_id = await self.user_session_repository.read_token(token)
        if not user_id:
            return None
        try:
            payload = jwt.decode_jwt(token, Config.JWT_TOKEN_SECRET)
            user_id_from_token = int(payload.get("user_id"))
        except Exception:
            return None
        if user_id_from_token != user_id:
            return None
        user = await self.user_repository.find_by_id(self.session, user_id)
        if not user:
            return None
        else:
            return user
