from typing import Optional

from fastapi import Form
from pydantic import BaseModel, EmailStr, Field, SecretStr

from app.core.schema.common_schemas import (
    ClientSecret,
    LoginType,
    ModelConfig,
    PasswordStr,
    PhoneStr,
)


class VerifyEmail(BaseModel):
    token: str = Field(description="token", example="token")

    class Config:
        schema_extra = {
            "description": "Email address verification",
            "example": {
                "token": "token",
            },
        }


class VerifyPhone(BaseModel):
    pin: str = Field(description="PIN", example="token")

    class Config:
        schema_extra = {
            "description": "Phone number verification",
            "example": {
                "pin": "123456",
            },
        }


class ForgotPasswordEmail(ClientSecret):
    email: EmailStr = Form()

    class Config(ModelConfig):
        schema_extra = {
            "description": "Reset password by email",
            "example": {
                "email": "user@example.com",
                "client_id": "client_id",
                "client_secret": "client_secret",
            },
        }


class ForgotPasswordPhone(ClientSecret):
    phone: PhoneStr = Form()

    class Config(ModelConfig):
        schema_extra = {
            "description": "Reset password by phone",
            "example": {
                "phone": "0969090658",
                "client_id": "client_id",
                "client_secret": "client_secret",
            },
        }


class BearerResponse(BaseModel):
    access_token: str
    token_type: str
    is_user_verified: bool


class ResetPassword(BaseModel):
    token: str = Field(description="token", example="token")
    password: SecretStr = Field(description="password", example="password")


class UserLogin(ClientSecret):
    email: Optional[EmailStr] = Form(default=None)
    phone: Optional[PhoneStr] = Form(default=None)
    facebook_id: Optional[str] = Form(
        description="Facebook id", example="facebook_id"
    )
    facebook_access_token: Optional[str] = Form(
        description="Facebook token", example="access_token"
    )
    google_id: Optional[str] = Form(
        description="Google id", example="google_id"
    )
    google_access_token: Optional[str] = Form(
        description="Access token", example="access_token"
    )

    password: Optional[PasswordStr] = Form()

    login_type: LoginType = Form(
        description="login type", example=LoginType.EMAIL
    )

    class Config(ModelConfig):
        schema_extra = {
            "description": "Reset password by email",
            "example": {
                "facebook_id": "101103474299404",
                "facebook_access_token": "41e142e15573b58e2c391116af606de8",
                "google_id": "101103474299404",
                "google_access_token": "41e142e15573b58e2c391116af606de8",
                "email": "user@example.com",
                "phone": "0969090658",
                "password": "password",
                "login_type": 1,
                "client_id": "client_id",
                "client_secret": "client_secret",
            },
        }


class UserFacebookLogin(ClientSecret):
    facebook_id: str = Field(description="Facebook id", example="facebook_id")
    facebook_access_token: str = Field(
        description="Facebook token", example="facebook_access_token"
    )

    class Config(ModelConfig):
        schema_extra = {
            "description": "Login by facebook",
            "example": {
                "facebook_id": "101103474299404",
                "facebook_access_token": "41e142e15573b58e2c391116af606de8",
                "client_id": "client_id",
                "client_secret": "client_secret",
            },
        }


class UserGoogleLogin(ClientSecret):
    google_id: str = Field(description="Google id", example="google_id")
    google_access_token: str = Field(
        description="Access token", example="google_access_token"
    )

    class Config(ModelConfig):
        schema_extra = {
            "description": "Login by google",
            "example": {
                "google_id": "101103474299404",
                "google_access_token": "41e142e15573b58e2c391116af606de8",
                "client_id": "client_id",
                "client_secret": "client_secret",
            },
        }
