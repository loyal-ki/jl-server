from typing import Protocol

import requests
from loguru import logger

from app.config.config import Config


class SMSSendFailed(Exception):
    pass


class SMSClient(Protocol):
    def send_sms(self, cellphone_number: str, text: str):
        ...  # pragma: no cover


class LoggingSMSClient(SMSClient):
    def send_sms(self, cellphone_number: str, text: str):
        logger.info(
            f"sent a SMS. cellphone_number={cellphone_number}, text={text}"
        )


class MediaSMSClient(SMSClient):
    def __init__(
        self,
        username: str = Config.MEDIA_SMS_USERNAME,
        password: str = Config.MEDIA_SMS_PASSWORD,
    ):
        self.username = username
        self.password = password

    def send_sms(self, cellphone_number: str, text: str):
        response: requests.Response = requests.post(
            url=Config.MEDIA_SMS_ENDPOINT,
            data={
                "username": self.username,
                "password": self.password,
                "mobilenumber": cellphone_number,
                "smstext": text,
            },
        )
        logger.info(f"sent a SMS. response={response.json()}")
        if response.status_code != 200:
            logger.error(
                f"SMS bounce occurred: status_code:{response.status_code}, response_json:{response.json()}"
            )
            raise SMSSendFailed()
