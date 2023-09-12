from enum import Enum
from typing import Optional

from fastapi import Form
from pydantic import BaseModel, SecretStr

from app.core.entities.user.user_entity import UserEntity


class ModelConfig:
    allow_population_by_field_name = True
    error_msg_templates = {
        "value_error.email": "Invalid email format",
        "value_error.missing": "This field is required",
        "value_error.any_str.max_length": "Please enter no more than {limit_value} characters",
        "value_error.date": "Please enter the date in the format YYYY-MM-dd",
        "type_error.none.not_allowed": "This field is required",
    }


class PasswordStr(SecretStr):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(
            pattern=UserEntity.PASSWORD_PATTERN,
            example=["a3qf83lSOk"],
        )

    @classmethod
    def validate(cls, v):
        # TypeError if v is not a string.
        if not isinstance(v, str):
            raise TypeError("string required")
        m = UserEntity.PASSWORD_PATTERN_COMPILED.fullmatch(v)
        # Raise ValueError if the string contains at least one
        # half width alphanumeric character between 8 and 20 characters.
        if not m:
            raise ValueError(
                """Contains at least one half-width alphanumeric character, between 8 and 20 characters."""
            )
        return v

    def __repr__(self):
        return f"PasswordStr({super().__repr__()})"


class PhoneStr(SecretStr):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(
            pattern=UserEntity.PHONE_PATTERN,
            example=["0969090658"],
        )

    @classmethod
    def validate(cls, v):
        # TypeError if v is not a string.
        if not isinstance(v, str):
            raise TypeError("string required")
        m = UserEntity.PHONE_PATTERN_COMPILED.fullmatch(v)
        # Check that the string is a 11 digit alphanumeric string.
        if not m:
            raise ValueError(
                "Not an 11-digit alphanumeric string starting with 03, 05, 07, 08, 09"
            )
        return v

    def __repr__(self):
        return f"PhoneStr({super().__repr__()})"


class LoginType(Enum):
    EMAIL = 1
    PHONE = 2
    FACEBOOK = 3
    GOOGLE = 4


class ClientSecret(BaseModel):
    client_id: Optional[str] = Form()
    client_secret: Optional[str] = Form()
