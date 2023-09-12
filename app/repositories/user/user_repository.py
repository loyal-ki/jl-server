from typing import Any, Optional

from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.entities.user.user_entity import UserEntity
from app.core.exceptions.user.user_exceptions import UserNotExists
from app.infra.dto.user.user_dto import UserDTO
from app.repositories.user.user_repository_protocol import (
    UserRepositoryProtocol,
)
from app.utils.logger import Log


class UserRepository(UserRepositoryProtocol):
    log = Log("UserRepository")

    async def create(
        self, session: AsyncSession, user: UserEntity
    ) -> UserEntity:
        user_dto = UserDTO.from_entity(user)
        session.begin_nested()
        session.add(user_dto)
        await session.commit()
        await session.refresh(user_dto)
        self.log.info(f"Created a user. id={user_dto.id}")
        return user_dto.to_entity()

    async def update(
        self, session: AsyncSession, user: UserEntity
    ) -> UserEntity:
        if user.id is None:
            raise ValueError

        user_dto: UserDTO = await self._find_by_id(session, user.id)
        if user_dto is None:
            raise UserNotExists
        session.begin_nested()
        user_dto.set_from_entity(user)
        await session.commit()
        await session.refresh(user_dto)
        self.log.info(f"Updated user to {user_dto.to_entity()}.")
        return user_dto.to_entity()

    async def find_by_id(
        self, session: AsyncSession, id: int
    ) -> Optional[UserEntity]:
        dto: UserDTO = await self._find_by_id(session, id)
        if dto is None:
            return None
        return dto.to_entity()

    async def find_by_email(
        self, session: AsyncSession, email: str
    ) -> Optional[UserEntity]:
        stmt = select(UserDTO).where(UserDTO.email == email)
        try:
            user_dto = await self._find_one(session, stmt)
        except NoResultFound:
            return None
        return user_dto.to_entity()

    async def find_by_phone(
        self, session: AsyncSession, phone: str
    ) -> Optional[UserEntity]:
        stmt = select(UserDTO).where(UserDTO.phone == phone)
        try:
            user_dto = await self._find_one(session, stmt)
        except NoResultFound:
            return None
        return user_dto.to_entity()

    async def find_by_facebook_id(
        self, session: AsyncSession, facebook_id: str
    ) -> Optional[UserEntity]:
        stmt = select(UserDTO).where(UserDTO.facebook_id == facebook_id)
        try:
            user_dto = await self._find_one(session, stmt)
        except NoResultFound:
            return None
        return user_dto.to_entity()

    async def find_by_user_code(
        self, session: AsyncSession, user_code: str
    ) -> Optional[UserEntity]:
        stmt = select(UserDTO).where(UserDTO.user_code == user_code)
        try:
            user_dto = await self._find_one(session, stmt)
        except NoResultFound:
            return None
        return user_dto.to_entity()

    async def _find_one(self, session: AsyncSession, stmt: Any) -> UserDTO:
        result = await session.execute(stmt)
        return result.scalar_one()

    async def _find_by_id(self, session: AsyncSession, id: int) -> UserDTO:
        stmt = select(UserDTO).where(UserDTO.id == id)
        try:
            return await self._find_one(session, stmt)
        except NoResultFound:
            return None
