import secrets
from typing import Optional

import redis.asyncio

from app.repositories.user.reset_repository import ResetRepositoryProtocol


class ResetRepository(ResetRepositoryProtocol):
    def __init__(
        self,
        redis: redis.asyncio.Redis,
        reset_session_token="reset_session_token:",
        lifetime_seconds=60 * 60 * 24,
    ):
        self.redis = redis
        self.reset_session_token = reset_session_token
        self.lifetime_seconds = lifetime_seconds

    async def read_token(self, token: str) -> Optional[str]:
        return await self.redis.get(f"{self.reset_session_token}{token}")

    async def write_token(self, user_id: str) -> str:
        token = secrets.token_urlsafe()
        await self.redis.set(
            f"{self.reset_session_token}{token}",
            user_id,
            ex=self.lifetime_seconds,
        )
        return token

    async def destroy_token(self, token: str) -> None:
        await self.redis.delete(f"{self.reset_session_token}{token}")
