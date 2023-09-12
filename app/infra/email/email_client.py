from typing import Optional, Protocol

import boto3
from loguru import logger

from app.config.config import Config


class EmailSendFailed(Exception):
    pass


class EmailClient(Protocol):
    def send_email(
        self,
        sender: str,
        to: list[str],
        reply_to: list[str],
        subject: str,
        text: str,
        html: Optional[str],
    ):
        ...  # pragma: no cover


class LoggingEmailClient(EmailClient):
    def send_email(
        self,
        sender: str,
        to: list[str],
        reply_to: list[str],
        subject: str,
        text: str,
        html: Optional[str] = None,
    ):
        logger.info(
            f"send email. sender:{sender}, to:{to}, reply_to: {reply_to}, subject:{subject}, text:{text}, html:{html}"
        )


class SESClient(EmailClient):
    def __init__(
        self,
        aws_access_key_id: str = Config.AWS_ACCESS_KEY_ID,
        aws_secret_access_key: str = Config.AWS_SECRET_ACCESS_KEY,
    ):
        logger.info(f"aws_access_key_id: {aws_access_key_id}")
        self.client = boto3.client(
            "ses",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name="ap-southeast-1",
        )

    def send_email(
        self,
        sender: str,
        to: list[str],
        reply_to: list[str],
        subject: str,
        text: str,
        html: Optional[str] = None,
    ):
        try:
            self.client.send_email(
                Destination={
                    "ToAddresses": to,
                },
                Message=self._message(subject, text, html),
                Source=sender,
                ReplyToAddresses=reply_to,
            )
        except Exception:
            logger.exception("Email send error occurred")
            raise EmailSendFailed()

    def _message(self, subject: str, text: str, html: Optional[str]) -> dict:
        message: dict = {
            "Body": {
                "Text": {
                    "Charset": "UTF-8",
                    "Data": text,
                },
            },
            "Subject": {
                "Charset": "UTF-8",
                "Data": subject,
            },
        }
        if html:
            message["Body"]["Html"] = {
                "Charset": "UTF-8",
                "Data": html,
            }
        return message
