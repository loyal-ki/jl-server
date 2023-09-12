from enum import Enum

from pydantic import BaseModel


class Error(BaseModel):
    code: str
    msg: str | None
    status: int | None

    def __init__(self, error: "ErrorCode") -> None:
        super().__init__(code=error.code, msg=error.msg, status=error.status)

    def get_code(self):
        return self.code

    def get_message(self):
        return self.msg

    def get_status(self):
        return self.status


class ErrorCode(str, Enum):
    code: str
    msg: str
    status: int

    def __new__(cls, code, msg, status) -> "ErrorCode":
        obj = str.__new__(cls, code)
        obj._value_ = code
        obj.code = code
        obj.msg = msg
        obj.status = status
        return obj

    VALIDATION_ERROR = ("VALIDATION_ERROR", "{0}", 400)

    INTERNAL_SERVER_ERROR = (
        "INTERNAL_SERVER_ERROR",
        "A system error has occurred.",
        500,
    )

    INVALID_CONTENT_TYPE = (
        "INVALID_CONTENT_TYPE",
        "Content-Type: application/json is required",
        400,
    )

    USER_DELETED = (
        "USER_DELETED",
        "User has been deleted.",
        400,
    )

    INVALID_PASSWORD = (
        "INVALID_PASSWORD",
        "Invalid password.",
        400,
    )

    USER_NOT_EXISTS = (
        "USER_NOT_EXISTS",
        "User not found.",
        400,
    )

    BAD_TOKEN = (
        "BAD_TOKEN",
        "The token is invalid.",
        400,
    )

    ALREADY_VERIFIED = (
        "ALREADY_VERIFIED",
        "Already verified.",
        400,
    )

    NOT_VERIFIED = (
        "NOT_VERIFIED",
        "Not verified yet.",
        400,
    )

    EMAIL_ALREADY_EXISTS = (
        "EMAIL_ALREADY_EXISTS",
        "Email address already exists.",
        400,
    )

    PHONE_ALREADY_EXISTS = (
        "PHONE_ALREADY_EXISTS",
        "Phone number already exists.",
        400,
    )

    LOGIN_USER_NOT_VERIFIED = (
        "LOGIN_USER_NOT_VERIFIED",
        "User is not verified yet.",
        400,
    )

    LOGIN_BAD_CREDENTIALS = (
        "LOGIN_BAD_CREDENTIALS",
        "Incorrect email address, phone number, or password.",
        400,
    )

    NOT_MATCH_CREDENTIALS = (
        "NOT_MATCH_CREDENTIALS",
        "The new passwords do not match.",
        400,
    )

    OLD_MATCHING_NEW_CREDENTIALS = (
        "OLD_MATCHING_NEW_CREDENTIALS",
        "For the new password, please set a password different from the current one.",
        400,
    )
    RESET_PASSWORD_BAD_TOKEN = (
        "RESET_PASSWORD_BAD_TOKEN",
        "Password reset token is invalid.",
        400,
    )

    TOO_MANY_REQUESTS = (
        "TOO_MANY_REQUESTS",
        "Too many requests.",
        400,
    )

    INVALID_CLIENT = (
        "INVALID_CLIENT",
        "Invalid client.",
        400,
    )

    REQUIRED_FACEBOOK_ID = (
        "REQUIRED_FACEBOOK_ID",
        "Facebook ID is required",
        400,
    )

    REQUIRED_FACEBOOK_ACCESS_TOKEN = (
        "REQUIRED_FACEBOOK_ACCESS_TOKEN",
        "Facebook access token is required",
        400,
    )

    REQUIRED_FACEBOOK_USER_NAME = (
        "REQUIRED_FACEBOOK_USER_NAME",
        "Facebook username is required",
        400,
    )

    ALREADY_EXISTS_FACEBOOK_ACCOUNT = (
        "ALREADY_EXISTS_FACEBOOK_ACCOUNT",
        "This Facebook user is already in use",
        400,
    )

    NOT_FOUND_FACEBOOK_USER = (
        "NOT_FOUND_FACEBOOK_USER",
        "Facebook user not found",
        404,
    )

    INVALID_FACEBOOK_ID_OR_TOKEN = (
        "INVALID_FACEBOOK_ID_OR_TOKEN",
        "Incorrect Facebook ID or Facebook access token",
        400,
    )

    REQUIRED_GOOGLE_ID = (
        "REQUIRED_FACEBOOK_ID",
        "Google ID is required",
        400,
    )

    REQUIRED_GOOGLE_ACCESS_TOKEN = (
        "REQUIRED_GOOGLE_ACCESS_TOKEN",
        "Google access token is required",
        400,
    )

    REQUIRED_GOOGLE_USER_NAME = (
        "REQUIRED_GOOGLE_USER_NAME",
        "Google username is required",
        400,
    )

    ALREADY_EXISTS_GOOGLE_ACCOUNT = (
        "ALREADY_EXISTS_GOOGLE_ACCOUNT",
        "This Google user is already in use",
        400,
    )

    NOT_FOUND_GOOGLE_USER = (
        "NOT_FOUND_GOOGLE_USER",
        "Google user not found",
        404,
    )

    INVALID_GOOGLE_ID_OR_TOKEN = (
        "INVALID_GOOGLE_ID_OR_TOKEN",
        "Incorrect Google ID or Google access token",
        400,
    )
