import dataclasses
import datetime
import random
import re
import string

import app.core.exceptions.user.user_exceptions as exception


@dataclasses.dataclass
class UserEntity:
    USER_CODE_LENGTH = 13

    hashed_password: str
    sex_code: str
    is_email_verified: bool = False
    is_phone_verified: bool = False
    is_facebook_verified: bool = False
    is_google_verified: bool = False

    id: int | None = None
    user_code: str | None = None
    email: str | None = None
    phone: str | None = None
    name: str | None = None
    birthday: datetime.date | None = None
    is_active: bool | None = None

    facebook_id: str | None = None
    facebook_access_token: str | None = None
    facebook_username: str | None = None

    google_id: str | None = None
    google_access_token: str | None = None
    google_username: str | None = None

    created_at: datetime.datetime | None = None
    updated_at: datetime.datetime | None = None
    deleted_at: datetime.datetime | None = None

    PASSWORD_PATTERN = r"^[A-Za-z0-9]{8,20}$"
    PASSWORD_PATTERN_COMPILED = re.compile(PASSWORD_PATTERN)
    PHONE_PATTERN = r"^(03|05|07|08|09)\d{8}$"
    PHONE_PATTERN_COMPILED = re.compile(PHONE_PATTERN)

    def __post__init__(self):
        self._validate_email_or_phone_required()

    def _validate_email_or_phone_required(self) -> bool:
        if not self.email and not self.phone:
            raise exception.EmailOrPhoneRequired
        return True

    def generate_user_code_if_empty(self):
        if self.user_code:
            return
        if not self.id:
            raise ValueError("id is required to generate user_code")

        id_str = str(self.id)
        padding_length = self.USER_CODE_LENGTH - 1 - len(id_str)
        padding = "".join(
            random.choices(
                string.ascii_letters + string.digits, k=padding_length
            )
        )
        self.user_code = f"{padding}_{id_str}"
