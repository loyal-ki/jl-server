from typing import Protocol

from app.core.entities.user.user_entity import UserEntity


class RefreshCountRepositoryProtocol(Protocol):
    async def write_count(self, user_entity: UserEntity) -> None:
        ...  # pragma: no cover

    async def read_count(self, user_entity: UserEntity) -> int:
        ...  # pragma: no cover

    async def destroy_count(self, user_entity: UserEntity) -> None:
        ...  # pragma: no cover
