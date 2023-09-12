import logging
import os
import sys
from pprint import pformat

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from loguru import logger
from loguru._defaults import LOGURU_FORMAT
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.errors import ServerErrorMiddleware

from app.config.config import Config
from app.core.exceptions import (
    DataConflictException,
    ForbiddenException,
    InternalServerError,
    NotFoundException,
    ServiceUnavailableException,
    UnauthorizedException,
)

if os.getenv("APP_ENV") == "production":
    journeyLingua = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
else:
    journeyLingua = FastAPI(title=Config.API_TITLE, version=Config.VERSION)

INFO_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> "
    "| <level>{level: <8}</level> | <cyan>File: {extra[filename]}</cyan> "
    "| Module: <cyan>{extra[business]}</cyan> | Function: <cyan>{extra[func]}</cyan> "
    "| Line: <cyan>{extra[line]}</cyan> | - <level>{message}</level>"
)

ERROR_FORMAT = (
    "<red>{time:YYYY-MM-DD HH:mm:ss.SSS}</red> "
    "| <level>{level: <8}</level> | <cyan>File: {extra[filename]}</cyan> "
    "| Module: <cyan>{extra[business]}</cyan> | Function: <cyan>{extra[func]}</cyan> "
    "| Line: <cyan>{extra[line]}</cyan> | - <level>{message}</level>"
)


@journeyLingua.exception_handler(ForbiddenException)
async def unexpected_exception_error(request: Request, exc: ForbiddenException):
    meta = {
        "code": exc.error_code,
        "msg": exc.message,
    }

    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content=jsonable_encoder(meta),
    )


@journeyLingua.exception_handler(UnauthorizedException)
async def unauthorized_error_handler(
    request: Request, exc: UnauthorizedException
):
    meta = {
        "code": exc.error_code,
        "msg": exc.message,
    }

    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content=jsonable_encoder(meta),
    )


@journeyLingua.exception_handler(DataConflictException)
async def data_conflict_error_handler(
    request: Request, exc: DataConflictException
):
    meta = {
        "code": exc.error_code,
        "msg": exc.message,
    }

    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content=jsonable_encoder(meta),
    )


@journeyLingua.exception_handler(NotFoundException)
async def not_supported_error_handler(request: Request, exc: NotFoundException):
    meta = {
        "code": exc.error_code,
        "msg": exc.message,
    }
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=jsonable_encoder(meta),
    )


@journeyLingua.exception_handler(ServiceUnavailableException)
async def service_unavailable_error_handler(
    request: Request, exc: ServiceUnavailableException
):
    meta = {
        "code": exc.error_code,
        "msg": exc.message,
    }
    return JSONResponse(
        status_code=status.HTTP_451_UNAVAILABLE_FOR_LEGAL_REASONS,
        content=jsonable_encoder(meta),
    )


async def global_execution_handler(request: Request, exc: InternalServerError):
    meta = {
        "code": exc.error_code,
        "msg": exc.message,
    }
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=jsonable_encoder(meta),
    )


# ADD GLOBAL ERROR
journeyLingua.add_middleware(
    ServerErrorMiddleware,
    handler=global_execution_handler,
)

# ADD CORS
journeyLingua.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class InterceptHandler(logging.Handler):
    """
    Default handler from examples in loguru documentaion.
    See https://loguru.readthedocs.io/en/stable/overview.html#entirely-compatible-with-standard-logging
    """

    def emit(self, record: logging.LogRecord):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno  # type: ignore

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back  # type: ignore
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def format_record(record: dict) -> str:
    format_string = LOGURU_FORMAT
    # Check if the log record has a "payload" in its "extra" dictionary
    if record["extra"].get("payload") is not None:
        # Format the "payload" using pformat with specific parameters
        record["extra"]["payload"] = pformat(
            record["extra"]["payload"], indent=4, compact=True, width=88
        )
        # Add the formatted payload to the format string
        format_string += "\n<level>{extra[payload]}</level>"

    # Add the "exception" information to the format string
    format_string += "{exception}\n"

    return format_string


def make_filter(name):
    def filter_(record):
        return record["extra"].get("name") == name

    return filter_


def init_logging():
    loggers = (
        logging.getLogger(name)
        for name in logging.root.manager.loggerDict
        if name.startswith("uvicorn.")
    )
    for uvicorn_logger in loggers:
        uvicorn_logger.handlers = []

    # change handler for default uvicorn logger
    intercept_handler = InterceptHandler()
    logging.getLogger("uvicorn").handlers = [intercept_handler]
    # set logs output, level and format
    # logger.add(sys.stdout, level=logging.DEBUG, format=format_record, filter=make_filter('stdout'))
    journey_lingua_info = os.path.join(
        Config.LOG_DIR, f"{Config.JOURNEY_LINGUA_INFO}.log"
    )
    journey_lingua_error = os.path.join(
        Config.LOG_DIR, f"{Config.JOURNEY_LINGUA_ERROR}.log"
    )
    logger.add(
        journey_lingua_info,
        enqueue=True,
        rotation="20 MB",
        level="DEBUG",
        filter=make_filter(Config.JOURNEY_LINGUA_INFO),
    )
    logger.add(
        journey_lingua_error,
        enqueue=True,
        rotation="10 MB",
        level="WARNING",
        filter=make_filter(Config.JOURNEY_LINGUA_ERROR),
    )
    logger.configure(
        handlers=[
            {
                "sink": sys.stdout,
                "level": logging.DEBUG,
                "format": format_record,
            },
            {
                "sink": journey_lingua_info,
                "level": logging.INFO,
                "format": INFO_FORMAT,
                "filter": make_filter(Config.JOURNEY_LINGUA_INFO),
            },
            {
                "sink": journey_lingua_error,
                "level": logging.WARNING,
                "format": ERROR_FORMAT,
                "filter": make_filter(Config.JOURNEY_LINGUA_ERROR),
            },
        ]
    )
    return logger
