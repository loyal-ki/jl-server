from app.core.entities.user.sex_entity import SexEntity
from app.infra.dto.user.sex_dto import SexDTO


class SeedDataSex:
    def table_name(self) -> str:
        return "sex"

    def data(self) -> list[SexDTO]:
        # @see https://ja.wikipedia.org/wiki/ISO_5218
        return [
            SexDTO(code=SexEntity.CODE_NOT_KNOWN, name="Unknown"),
            SexDTO(code=SexEntity.CODE_MALE, name="Male"),
            SexDTO(code=SexEntity.CODE_FEMALE, name="Female"),
        ]
