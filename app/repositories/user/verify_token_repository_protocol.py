from typing import Optional, Protocol

from app.core.entities.user.user_entity import UserEntity

class VerifyTokenRepositoryProtocol(Protocol):
    async def write_email_token(self, user_entity: UserEntity) -> str:
        ...  # pragma: no cover

    async def write_phone_pin_code(self, user_entity: UserEntity) -> str:
        ...  # pragma: no cover

    async def read_token(self, token: str) -> Optional[str]:
        ...  # pragma: no cover

    async def destroy_token(self, token: str) -> None:
        ...  # pragma: no cover
