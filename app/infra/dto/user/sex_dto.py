from sqlalchemy import CHAR, Column, String

from app.core.database import Base
from app.core.entities.user.sex_entity import SexEntity

class SexDTO(Base):
    __tablename__ = "sex"

    code: str | Column = Column(CHAR(1), primary_key=True, nullable=False)
    name: str | Column = Column(String(10), nullable=False)

    def to_entity(self) -> SexEntity:
        return SexEntity(
            code=self.code,
            name=self.name,
        )

    @staticmethod
    def from_entity(sex: SexEntity) -> "SexDTO":
        return SexDTO(
            code=sex.code,
            name=sex.name,
        )
