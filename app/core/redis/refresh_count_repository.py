import redis.asyncio
import redis.exceptions

from app.core.entities.user.user_entity import UserEntity
from app.repositories.user.refresh_count_repository import (
    RefreshCountRepositoryProtocol,
)


class RefreshCountRepository(RefreshCountRepositoryProtocol):
    def __init__(
        self,
        redis: redis.asyncio.Redis,
        token_prefix="refresh_count:",
        lifetime_seconds=60 * 60 * 24,
    ):
        self.redis = redis
        self.token_prefix = token_prefix
        self.lifetime_seconds = lifetime_seconds

    async def write_count(self, user_entity: UserEntity, count: int) -> None:
        """
        Save the refresh count in Redis for a 24-hour period.
        """
        count_key = f"{self.token_prefix}{str(user_entity.id)}"
        await self.redis.set(
            count_key,
            str(count),
            ex=self.lifetime_seconds,
        )

    async def read_count(self, user_entity: UserEntity) -> int:
        count = await self.redis.get(f"{self.token_prefix}{user_entity.id}")
        # Return the number of times the number of times
        if count is None:
            return 0
        else:
            return int(count)

    async def destroy_count(self, user_entity: UserEntity) -> None:
        """
        @brief Destroy the count of a user.
        """
        count = await self.read_count(user_entity)
        # Delete the user entity from redis.
        if count > 0:
            await self.redis.delete(f"{self.token_prefix}{user_entity.id}")
