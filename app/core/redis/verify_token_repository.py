import random
import secrets
import string
from typing import Optional

import redis.asyncio
import redis.exceptions

from app.core.entities.user.user_entity import UserEntity
from app.repositories.user.verify_token_repository_protocol import (
    VerifyTokenRepositoryProtocol,
)


class VerifyTokenRepository(VerifyTokenRepositoryProtocol):
    def __init__(
        self,
        redis: redis.asyncio.Redis,
        token_prefix="verify_token:",
        lifetime_seconds=60 * 60 * 24,
    ):
        self.redis = redis
        self.token_prefix = token_prefix
        self.lifetime_seconds = lifetime_seconds

    async def write_email_token(self, user_entity: UserEntity) -> str:
        """
        Generate a token and store it in Redis for a 24-hour period.
        """
        # if user_entity. email is not set
        if not user_entity.email:
            raise ValueError("email is required")

        token = secrets.token_urlsafe()
        await self.redis.set(
            f"{self.token_prefix}{token}",
            user_entity.email,
            ex=self.lifetime_seconds,
        )
        return token

    async def write_phone_pin_code(self, user_entity: UserEntity) -> str:
        """
        Generate a PIN code and store it in Redis for a 24-hour period.
        """
        # if phone is not set.
        if not user_entity.phone:
            raise ValueError("phone is required")

        # Generate a PIN code randomly and save it
        # Regenerate it if it already exists
        # Returns a random token for a random number of random numbers.
        for _ in range(50):  # Set an upper limit just in case
            pin = "".join(random.choices(string.digits, k=6))
            key = f"{self.token_prefix}{pin}"
            # Returns True if set, or None if already exists
            set = await self.redis.set(
                key,
                user_entity.phone,
                ex=self.lifetime_seconds,
                nx=True,
            )
            # If set is set continue to the next call to set.
            if not set:
                continue
            return pin
        raise Exception("Failed to generate a PIN code")

    async def read_token(self, token: str) -> Optional[str]:
        return await self.redis.get(f"{self.token_prefix}{token}")

    async def destroy_token(self, token: str) -> None:
        await self.redis.delete(f"{self.token_prefix}{token}")
