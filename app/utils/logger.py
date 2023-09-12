import inspect
import os

from loguru import logger

from app.config.config import Config


class Log(object):
    business = None

    def __init__(self, name="journeyLingua"):
        if not os.path.exists(Config.LOG_DIR):
            os.mkdir(Config.LOG_DIR)
        self.business = name

    def info(self, message: str):
        file_name, line, func, _, _ = inspect.getframeinfo(
            inspect.currentframe().f_back
        )
        logger.bind(
            name=Config.JOURNEY_LINGUA_INFO,
            func=func,
            line=line,
            business=self.business,
            filename=file_name,
        ).debug(message)

    def error(self, message: str):
        file_name, line, func, _, _ = inspect.getframeinfo(
            inspect.currentframe().f_back
        )
        logger.bind(
            name=Config.JOURNEY_LINGUA_ERROR,
            func=func,
            line=line,
            business=self.business,
            filename=file_name,
        ).error(message)

    def warning(self, message: str):
        file_name, line, func, _, _ = inspect.getframeinfo(
            inspect.currentframe().f_back
        )
        logger.bind(
            name=Config.JOURNEY_LINGUA_ERROR,
            func=func,
            line=line,
            business=self.business,
            filename=file_name,
        ).warning(message)

    def debug(self, message: str):
        file_name, line, func, _, _ = inspect.getframeinfo(
            inspect.currentframe().f_back
        )
        logger.bind(
            name=Config.JOURNEY_LINGUA_INFO,
            func=func,
            line=line,
            business=self.business,
            filename=file_name,
        ).debug(message)

    def exception(self, message: str):
        file_name, line, func, _, _ = inspect.getframeinfo(
            inspect.currentframe().f_back
        )
        logger.bind(
            name=Config.JOURNEY_LINGUA_ERROR,
            func=func,
            line=line,
            business=self.business,
            filename=file_name,
        ).exception(message)
