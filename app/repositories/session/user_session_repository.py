from typing import Optional

import redis.asyncio

from app.config.config import Config
from app.core.entities.user.user_entity import UserEntity
from app.core.schema.common_schemas import LoginType
from app.helpers import jwt
from app.repositories.session.user_session_repository_protocol import (
    UserSessionRepositoryProtocol,
)


class UserSessionRepository(UserSessionRepositoryProtocol):
    def __init__(
        self, redis: redis.asyncio.Redis, session_token="user_session_token:"
    ):
        self.redis = redis
        self.session_token = session_token

    async def read_token(self, token: str) -> Optional[int]:
        user_id = await self.redis.get(f"{self.session_token}{token}")
        if user_id is None:
            return None

        return int(user_id)

    async def write_token(self, user: UserEntity, login_type: LoginType) -> str:
        data = {}
        if login_type is LoginType.EMAIL:
            data.update({"email": user.email})
        elif login_type is LoginType.PHONE:
            data.update({"phone": user.phone})
        elif login_type is LoginType.FACEBOOK:
            data.update({"facebook_id": user.facebook_id})
        elif login_type is LoginType.GOOGLE:
            data.update({"google_id": user.google_id})
        data.update({"user_id": str(user.id)})
        token = jwt.generate_jwt(
            data,
            Config.JWT_TOKEN_SECRET,
            Config.JWT_AUD_CREATE,
            Config.JWT_TOKEN_EXPIRATION_DAY,
            Config.JWT_ALGORITHM,
        )
        await self.redis.set(f"{self.session_token}{token}", str(user.id))
        return token

    async def destroy_token(self, token: str) -> None:
        await self.redis.delete(f"{self.session_token}{token}")
