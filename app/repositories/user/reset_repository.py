from typing import Optional, Protocol


class ResetRepositoryProtocol(Protocol):
    async def write_token(self, user_id: str) -> str:
        ...  # pragma: no cover

    async def read_token(self, token: str) -> Optional[str]:
        ...  # pragma: no cover

    async def destroy_token(self, token: str) -> None:
        ...  # pragma: no cover
