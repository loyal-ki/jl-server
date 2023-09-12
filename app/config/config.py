import os
from enum import Enum
from pathlib import Path
from typing import List

from pydantic import BaseSettings

ROOT = Path(__file__).parent.parent.parent

print(ROOT)


class BaseConfig(BaseSettings):
    # APP
    APP_ENV: str = "local"
    VERSION: str = "0.0.1"
    API_TITLE: str = ""
    REFRESH_COUNT_LIMIT: int = 10

    LOG_DIR = os.path.join(ROOT, "logs")
    LOG_NAME = os.path.join(LOG_DIR, "journey_lingua.log")

    # SERVER
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int

    # MOCK SERVER
    MOCK_ON: bool
    PROXY_ON: bool
    PROXY_PORT: int

    # MYSQL
    MYSQL_HOST: str
    MYSQL_PORT: str
    MYSQL_USER: str
    MYSQL_PASSWORD: str
    MYSQL_DB_NAME: str
    MYSQL_TEST_DB_NAME: str = "journey_lingua_test"

    # SQLALCHEMY
    SQL_ALCHEMY_DATABASE_URI: str = ""
    ASYNC_SQL_ALCHEMY_URI: str = ""

    # REDIS
    REDIS_ON: bool
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int
    REDIS_PASSWORD: str
    REDIS_NODES: List[dict] = []

    # CLIENT_ID
    CLIENT_ID: str
    CLIENT_SECRET: str

    # RETRY
    RETRY_TIMES = 1

    # AWS
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str

    # LOG
    JOURNEY_LINGUA_ERROR = "JOURNEY_LINGUA_ERROR"
    JOURNEY_LINGUA_INFO = "JOURNEY_LINGUA_INFO"

    # JWT
    JWT_ALGORITHM: str = "HS256"
    JWT_AUD_CREATE: str = "journey_lingua:create"
    JWT_AUD_VERIFY: str = "journey_lingua:verify"
    JWT_AUD_RESET: str = "journey_lingua:reset"
    JWT_TOKEN_SECRET: str
    JWT_TOKEN_EXPIRATION_DAY: int = 180

    # SMS
    MEDIA_SMS_ENDPOINT: str = "https://www.sms-ope.com/sms/api/"
    MEDIA_SMS_USERNAME: str
    MEDIA_SMS_PASSWORD: str

    # MAIL
    MAIL_SENDER: str = "leminhtrungnghia8991@gmail.com"
    MAIL_REPLY_TO: str = "leminhtrungnghia8991@gmail.com"

    # DYNAMIC LINK
    DYNAMIC_LINK_ROOT: str = ""
    DYNAMIC_LINK_LINK: str = ""
    DYNAMIC_LINK_APN: str = ""
    DYNAMIC_LINK_AFL: str = ""
    DYNAMIC_LINK_ISI: str = ""
    DYNAMIC_LINK_IBI: str = ""
    DYNAMIC_LINK_IFL: str = ""
    DYNAMIC_LINK_EFL: int = 1
    DYNAMIC_LINK_API_URL: str = ""
    FIREBASE_API_KEY: str = ""

    # FACEBOOK
    FACEBOOK_CLIENT_ID: str = ""
    FACEBOOK_CLIENT_SECRET: str = ""

    # GOOGLE
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""


class DevConfig(BaseConfig):
    class Config:
        env_file = os.path.join(ROOT, "conf", "dev.env")


class ProConfig(BaseConfig):
    class Config:
        env_file = os.path.join(ROOT, "conf", "pro.env")


JOURNEY_LINGUA_ENV = os.environ.get("journey_lingua_env", "dev")

Config = (
    ProConfig()
    if JOURNEY_LINGUA_ENV and JOURNEY_LINGUA_ENV.lower() == "pro"
    else DevConfig()
)

Config.REDIS_NODES = [
    {
        "host": Config.REDIS_HOST,
        "port": Config.REDIS_PORT,
        "db": Config.REDIS_DB,
        "password": Config.REDIS_PASSWORD,
    }
]


class AppEnv(str, Enum):
    local = "local"
    staging = "staging"
    prod = "production"


# pylint: disable=anomalous-backslash-in-string
BANNER = """
       _  ____  _    _ _____  _   _ ________     __      _      _____ _   _  _____ _    _         
      | |/ __ \| |  | |  __ \| \ | |  ____\ \   / /     | |    |_   _| \ | |/ ____| |  | |  /\    
      | | |  | | |  | | |__) |  \| | |__   \ \_/ /      | |      | | |  \| | |  __| |  | | /  \   
  _   | | |  | | |  | |  _  /| . ` |  __|   \   /       | |      | | | . ` | | |_ | |  | |/ /\ \  
 | |__| | |__| | |__| | | \ \| |\  | |____   | |        | |____ _| |_| |\  | |__| | |__| / ____ \ 
  \____/ \____/ \____/|_|  \_\_| \_|______|  |_|        |______|_____|_| \_|\_____|\____/_/    \_\                                                                                      
"""
# pylint: disable=anomalous-backslash-in-string
