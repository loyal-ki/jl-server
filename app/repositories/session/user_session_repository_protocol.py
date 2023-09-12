from typing import Protocol

from app.core.entities.user.user_entity import UserEntity
from app.core.schema.common_schemas import LoginType


class UserSessionRepositoryProtocol(Protocol):
    async def read_token(self, token: str) -> UserEntity:
        ...  # pragma: no cover

    async def write_token(self, user: UserEntity, login_type: LoginType) -> str:
        ...  # pragma: no cover

    async def destroy_token(self, token: str) -> str:
        ...  # pragma: no cover
