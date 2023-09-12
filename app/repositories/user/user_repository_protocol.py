from typing import Optional, Protocol

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.entities.user.user_entity import UserEntity


class UserRepositoryProtocol(Protocol):
    async def find_by_id(
        self, session: AsyncSession, id: int
    ) -> Optional[UserEntity]:
        ...  # pragma: no cover

    async def find_by_email(
        self, session: AsyncSession, email: str
    ) -> Optional[UserEntity]:
        ...  # pragma: no cover

    async def find_by_phone(
        self, session: AsyncSession, phone: str
    ) -> Optional[UserEntity]:
        ...  # pragma: no cover

    async def find_by_facebook_id(
        self, session: AsyncSession, facebook_id: str
    ) -> Optional[UserEntity]:
        ...  # pragma: no cover

    async def find_by_google_id(
        self, session: AsyncSession, google_id: str
    ) -> Optional[UserEntity]:
        ...  # pragma: no cover

    async def find_by_user_code(
        self, session: AsyncSession, user_code: str
    ) -> Optional[UserEntity]:
        ...  # pragma: no cover

    async def create(
        self, session: AsyncSession, user: UserEntity
    ) -> UserEntity:
        ...  # pragma: no cover

    async def update(
        self, session: AsyncSession, user: UserEntity
    ) -> UserEntity:
        ...  # pragma: no cover
