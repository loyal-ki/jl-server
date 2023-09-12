from datetime import date
from enum import Enum

from fastapi import Form
from pydantic import BaseModel, EmailStr, Field, SecretStr

from app.core.entities.user.sex_entity import SexEntity
from app.core.entities.user.user_entity import UserEntity
from app.core.schema.common_schemas import (
    ClientSecret,
    ModelConfig,
    PasswordStr,
    PhoneStr,
)


class UserEmailCreate(ClientSecret):
    email: EmailStr = Form()
    password: PasswordStr = Form()

    class Config(ModelConfig):
        schema_extra = {
            "description": "Register using email address",
            "example": {
                "email": "user@example.com",
                "password": "password",
                "client_id": "client_id",
                "client_secret": "client_secret",
            },
        }


class UserPhoneCreate(ClientSecret):
    phone: PhoneStr = Form()
    password: PasswordStr = Form()

    class Config(ModelConfig):
        schema_extra = {
            "description": "Register using phone number",
            "example": {
                "phone": "0969090658",
                "password": "password",
                "client_id": "client_id",
                "client_secret": "client_secret",
            },
        }


class UserFacebookCreate(ClientSecret):
    facebook_id: str = Field(title="facebook id", example="101103474299404")
    facebook_access_token: str = Field(
        title="Facebook access token",
        example="41e142e15573b58e2c391116af606de8",
    )

    class Config:
        schema_extra = {
            "description": "Register using facebook",
            "example": {
                "facebook_id": "101103474299404",
                "facebook_access_token": "41e142e15573b58e2c391116af606de8",
                "client_id": "client_id",
                "client_secret": "client_secret",
            },
        }


class UserGoogleCreate(ClientSecret):
    google_id: str = Field(title="Google id", example="101103474299404")
    google_access_token: str = Field(
        title="Google access token",
        example="41e142e15573b58e2c391116af606de8",
    )

    class Config:
        schema_extra = {
            "description": "Register using google",
            "example": {
                "google_id": "101103474299404",
                "google_access_token": "41e142e15573b58e2c391116af606de8",
                "client_id": "client_id",
                "client_secret": "client_secret",
            },
        }


class UserEmailUpdate(BaseModel):
    email: EmailStr = Field(title="Email Address", example="user@example.com")

    class Config:
        schema_extra = {
            "description": "Update email address",
            "example": {
                "email": "user@example.com",
            },
        }


class UserPhoneUpdate(BaseModel):
    phone: PhoneStr = Field(title="Phone Number", example="0969090658")

    class Config:
        schema_extra = {
            "description": "Update phone number",
            "example": {
                "phone": "0969090658",
            },
        }


class UserPasswordUpdate(BaseModel):
    old_password: SecretStr = Field(
        description="Old Password", example="password"
    )
    new_password: SecretStr = Field(
        description="New Password", example="password"
    )
    new_password_confirm: SecretStr = Field(
        description="Confirm New Password", example="password"
    )


class UserRead(BaseModel):
    user_id: int = Field(title="User ID", example=1)
    user_code: str = Field(title="User Code", example="1234567890")
    email: EmailStr | None = Field(
        title="Email Address", example="user@example.com"
    )
    phone: str | None = Field(title="Phone Number", example="0969090658")
    name: str | None = Field(title="Name", example="John Doe")
    sex: "Sex" = Field(title="Sex", example="male")
    birthday: date | None = Field(title="Birthday", example="01-01-1999")

    facebook_id: str | None = Field(title="Facebook id", example="")
    facebook_access_token: str | None = Field(
        title="Facebook access token", example=""
    )
    facebook_username: str | None = Field(title="Facebook username", example="")

    google_id: str | None = Field(title="Google id", example="")
    google_access_token: str | None = Field(
        title="Google access token", example=""
    )
    google_username: str | None = Field(title="Google username", example="")

    is_email_verified: bool | None = Field(title="Email Verified", example=True)
    is_phone_verified: bool | None = Field(title="Phone Verified", example=True)
    is_active: bool = Field(title="Account Active", example=True)

    class Config:
        use_enum_values = True

    @staticmethod
    def from_entity(user: UserEntity) -> "UserRead":
        return UserRead(
            user_id=user.id,
            user_code=user.user_code,
            email=user.email,
            phone=user.phone,
            name=user.name,
            sex=Sex.from_code(user.sex_code),
            birthday=user.birthday,
            facebook_id=user.facebook_id,
            facebook_access_token=user.facebook_access_token,
            facebook_username=user.facebook_username,
            google_id=user.google_id,
            google_access_token=user.google_access_token,
            google_username=user.google_username,
            is_email_verified=user.is_email_verified,
            is_phone_verified=user.is_phone_verified,
            is_active=user.is_active,
        )


class UserUpdate(BaseModel):
    name: str = Field(description="Name", example="John Doe", max_length=50)
    sex: "Sex" = Field(description="Sex", example="male")
    birthday: date = Field(description="Birthday", example="1999-01-01")

    class Config(ModelConfig):
        error_msg_templates = ModelConfig.error_msg_templates | {
            "type_error.enum": "Please enter one of the following values: not_known, male, female",
        }
        use_enum_values = True

    @staticmethod
    def from_entity(user: UserEntity) -> "UserRead":
        return UserRead(
            user_id=user.id,
            user_code=user.user_code,
            email=user.email,
            phone=user.phone,
            is_email_verified=user.is_email_verified,
            is_phone_verified=user.is_phone_verified,
            is_active=user.is_active,
        )


class Sex(str, Enum):
    not_known = "not_known"
    male = "male"
    female = "female"

    @staticmethod
    def from_code(sex_code) -> "Sex":
        if sex_code == SexEntity.CODE_NOT_KNOWN:
            return Sex.not_known
        elif sex_code == SexEntity.CODE_MALE:
            return Sex.male
        elif sex_code == SexEntity.CODE_FEMALE:
            return Sex.female
        else:
            raise ValueError

    @staticmethod
    def to_code(sex_name: str) -> str:
        if sex_name == Sex.not_known:
            return SexEntity.CODE_NOT_KNOWN
        elif sex_name == Sex.male:
            return SexEntity.CODE_MALE
        elif sex_name == Sex.female:
            return SexEntity.CODE_FEMALE
        else:
            raise ValueError


UserRead.update_forward_refs()
UserUpdate.update_forward_refs()
