from typing import Protocol

import facebook
from loguru import logger

import app.core.exceptions.user.user_exceptions as exception
from app.config.config import AppEnv, Config


class FacebookClientProtocol(Protocol):
    async def is_valid_access_token(
        self,
        facebook_id: str,
        access_token: str,
    ) -> bool:
        ...  # pragma: no cover

    async def get_facebook_id(
        self,
        access_token: str,
    ) -> str:
        ...  # pragma: no cover


class FacebookClient(FacebookClientProtocol):
    async def is_valid_access_token(
        self, facebook_id: str, access_token: str
    ) -> bool:
        """
        Check if the access token is valid for the given Facebook ID.

        Args:
            facebook_id (str): The Facebook ID of the user.
            access_token (str): The access token to be validated.

        Returns:
            bool: True if the access token is valid, False otherwise.
        """
        # If running in local environment, always return True
        if Config.APP_ENV == AppEnv.local:
            return True

        # Create a Facebook GraphAPI instance
        graph = facebook.GraphAPI()  # type: ignore

        # Debug the access token with Facebook's API
        response = graph.debug_access_token(
            token=access_token,
            app_id=Config.FACEBOOK_CLIENT_ID,
            app_secret=Config.FACEBOOK_CLIENT_SECRET,
        )

        # Log the response
        logger.debug(response)

        logger.info(f"facebook response: {response}")

        # If the response is empty, the credentials are not verified
        if not response:
            logger.warning("Not verify credentials.")
            return False

        # Check if the access token is valid
        data = response.get("data")
        if not data.get("is_valid"):
            logger.warning("not verify credentials.")
            return False

        facebook_id_from_access_token = data.get("user_id")

        # Check if the Facebook ID in the access token matches the provided Facebook ID
        if facebook_id != facebook_id_from_access_token:
            logger.warning(
                f"different facebook id. facebook_id_from_arg => {facebook_id} facebook_id_from_access_token => {facebook_id_from_access_token}"  # noqa: E501
            )
            return False

        # If all checks pass, the access token is valid
        return True

    async def get_facebook_id(self, access_token: str) -> str:
        """
        Get the Facebook ID associated with a given Facebook ID and access token.

        Args:
            facebook_id (str): The Facebook ID.
            access_token (str): The access token.

        Returns:
            str: The Facebook ID obtained from the access token.

        Raises:
            exception.InvalidFacebookAccessToken: If the access token is invalid.

        """
        # Create a GraphAPI object
        graph = facebook.GraphAPI()  # type: ignore

        # Use the access token to debug and verify it
        response = graph.debug_access_token(
            token=access_token,
            app_id=Config.FACEBOOK_CLIENT_ID,
            app_secret=Config.FACEBOOK_CLIENT_SECRET,
        )
        logger.debug(response)

        # Check if the access token is valid
        if not response:
            logger.warning("not verify credentials.")
            raise exception.InvalidFacebookAccessToken

        # Get the user data from the response
        data = response.get("data")

        # Check if the access token is valid
        if not data.get("is_valid"):
            logger.warning("not verify credentials.")
            raise exception.InvalidFacebookAccessToken

        # Get the Facebook ID from the access token
        facebook_id_from_access_token = data.get("user_id")

        return facebook_id_from_access_token
