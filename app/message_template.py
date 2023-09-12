# flake8: noqa
from urllib.parse import quote

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from app.config.config import Config


class MessageTemplate:
    @staticmethod
    def _long_link_generator(path_and_query: str) -> str:
        return (
            f"{Config.DYNAMIC_LINK_ROOT}/?link={Config.DYNAMIC_LINK_LINK}{path_and_query}"
            + f"&apn={Config.DYNAMIC_LINK_APN}&afl={Config.DYNAMIC_LINK_AFL}"
            + f"&isi={Config.DYNAMIC_LINK_ISI}&ibi={Config.DYNAMIC_LINK_IBI}&ifl={Config.DYNAMIC_LINK_IFL}"
        )

    @staticmethod
    def _short_link_generator(path_and_query: str) -> str:
        payload = {
            "dynamicLinkInfo": {
                "domainUriPrefix": Config.DYNAMIC_LINK_ROOT,
                "link": f"{Config.DYNAMIC_LINK_LINK}{path_and_query}",
                "androidInfo": {
                    "androidPackageName": Config.DYNAMIC_LINK_APN,
                    "androidFallbackLink": Config.DYNAMIC_LINK_AFL,
                },
                "iosInfo": {
                    "iosBundleId": Config.DYNAMIC_LINK_IBI,
                    "iosFallbackLink": Config.DYNAMIC_LINK_IFL,
                    "iosAppStoreId": Config.DYNAMIC_LINK_ISI,
                },
                "navigationInfo": {
                    "enableForcedRedirect": Config.DYNAMIC_LINK_EFL,
                },
            },
            "suffix": {"option": "SHORT"},
        }
        headers = {"Content-Type": "application/json"}

        retry = Retry(
            total=3, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry)
        session = requests.Session()

        session.mount("http://", adapter)
        session.mount("https://", adapter)
        try:
            response = session.post(
                Config.DYNAMIC_LINK_API_URL, json=payload, headers=headers
            )
            response.raise_for_status()
        except Exception as e:
            raise e
        response_json = response.json()
        # shortLink is not found in response_json
        if not response_json["shortLink"]:
            raise Exception("shortLink is not found")
        return response_json["shortLink"]

    @staticmethod
    def _formatter(text: str) -> str:
        """Remove the indent"""
        return "\n".join([line.lstrip() for line in text.split("\n")])

    @classmethod
    def verify_email_text(cls, token: str) -> str:
        path_and_query = quote(
            f"/auth/verify/email?token={token}&type=verify", safe="/?"
        )
        text = f"""
        Thank you for registering with Journey Lingua App.

        Please click the URL below to complete your registration:

        ▼ Registration URL
        {cls._long_link_generator(path_and_query)}

        * This URL is valid for 24 hours.
        * If the URL expires, please go through the temporary registration process again.
        * If you do not recognize this email, please disregard it.

        ━━━━━━━━━━━━━
        Journey Lingua Corporation
        https://www.journeylingua.com/en/us

        Contact Us
        {Config.MAIL_REPLY_TO}

        * This email address is for sending purposes only and we cannot respond to any replies. Thank you for your understanding.

        """
        return cls._formatter(text)

    @classmethod
    def verify_sms_text(cls, pin: str) -> str:
        return f"The authentication code for the Journey Lingua app is {pin}. It is valid for 24 hours."

    @classmethod
    def reset_email_text(cls, token: str) -> str:
        path_and_query = quote(f"/auth/reset-password?token={token}", safe="/?")
        text = f"""
        Thank you for using Journey Lingua App.

        Please click the URL below to reset your password:

        ▼ Reset Password URL
        {cls._long_link_generator(path_and_query)}

        * This URL is valid for 24 hours.
        * If the URL expires, please go through the password reset process again.
        * If you do not recognize this email, please disregard it.

        ━━━━━━━━━━━━━
        Journey Lingua Corporation
        https://www.journeylingua.com/en/us

        Contact Us
        {Config.MAIL_REPLY_TO}

        * This email address is for sending purposes only and we cannot respond to any replies. Thank you for your understanding.
        """
        return cls._formatter(text)

    @classmethod
    def reset_sms_text(cls, token: str) -> str:
        path_and_query = f"/auth/reset-password?token={token}"
        text = f"""
        ▼ Reset your Journey Lingua App password
        {cls._short_link_generator(path_and_query)}
        """
        return cls._formatter(text)

    @classmethod
    def update_email_text(cls, token: str) -> str:
        path_and_query = quote(
            f"/auth/verify/email?token={token}&type=update", safe="/?"
        )
        text = f"""
        Thank you for registering with Journey Lingua App.

        Please click the URL below to complete the email address change process:

        ▼ Email Address Change URL
        {cls._long_link_generator(path_and_query)}

        * This URL is valid for 24 hours.
        * If the URL expires, please go through the email address change process again.
        * If you do not recognize this email, please disregard it.

        ━━━━━━━━━━━━━
        Journey Lingua Corporation
        https://www.journeylingua.com/en/us

        Contact Us
        {Config.MAIL_REPLY_TO}

        * This email address is for sending purposes only and we cannot respond to any replies. Thank you for your understanding.
        """
        return cls._formatter(text)
