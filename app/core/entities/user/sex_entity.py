import dataclasses


@dataclasses.dataclass
class SexEntity:
    code: str
    name: str

    CODE_NOT_KNOWN = "0"
    CODE_MALE = "1"
    CODE_FEMALE = "2"
