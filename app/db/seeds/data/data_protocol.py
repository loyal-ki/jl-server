from typing import Protocol, TypeVar

from app.core.database import Base

BaseT = TypeVar("BaseT", bound=Base)


class SeedDataProtocol(Protocol):
    def table_name(self) -> str:
        ...  # pragma: no cover

    def data(self) -> list[BaseT]:
        ...  # pragma: no cover
