from typing import Protocol

from sqlalchemy.orm import Session

from app.repositories.session.user_session_repository_protocol import (
    UserSessionRepositoryProtocol,
)
from app.repositories.user.user_repository_protocol import (
    UserRepositoryProtocol,
)


class LogoutUseCase(Protocol):
    async def logout(self, token: str) -> None:
        ...  # pragma: no cover


class LogoutInteractor(LogoutUseCase):
    def __init__(
        self,
        user_repository: UserRepositoryProtocol,
        user_session_repository: UserSessionRepositoryProtocol,
        session: Session,
    ):
        self.user_repository = user_repository
        self.user_session_repository = user_session_repository
        self.session = session

    async def logout(self, token: str) -> None:
        await self.user_session_repository.destroy_token(token)
