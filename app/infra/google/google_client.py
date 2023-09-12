from typing import Protocol

from google.auth.transport import requests
from google.oauth2 import id_token
from loguru import logger

import app.core.exceptions.user.user_exceptions as exception
from app.config.config import AppEnv, Config


class GoogleClientProtocol(Protocol):
    async def is_valid_access_token(
        self,
        google_id: str,
        access_token: str,
    ) -> bool:
        ...  # pragma: no cover

    async def get_google_id(
        self,
        access_token: str,
    ) -> str:
        ...  # pragma: no cover


class GoogleClient(GoogleClientProtocol):
    async def is_valid_access_token(
        self,
        google_id: str,
        access_token: str,
    ) -> bool:
        try:
            # If running in local environment, always return True
            if Config.APP_ENV == AppEnv.local:
                return True

            id_info = id_token.verify_oauth2_token(
                access_token, requests.Request(), Config.GOOGLE_CLIENT_ID
            )

            user_id = id_info["sub"]

            if google_id != user_id:
                logger.warning(
                    f"different google id. google_id_from_arg => {google_id} google_id_from_access_token => {user_id}"
                )
                return False

            return True

        except Exception:
            raise exception.InvalidGoogleAccessToken

    async def get_google_id(
        self,
        access_token: str,
    ) -> str:
        try:
            id_info = id_token.verify_oauth2_token(
                access_token, requests.Request(), Config.GOOGLE_CLIENT_ID
            )
            user_id = id_info["sub"]
            return user_id

        except Exception:
            raise exception.InvalidGoogleAccessToken
