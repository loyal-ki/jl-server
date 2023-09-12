from fastapi import Request

from app.config.config import BANNER, JOURNEY_LINGUA_ENV, Config
from app.core.redis.redis import get_redis
from app.initialize import init_logging, journeyLingua
from app.routers.auth import (
    login_route,
    logout_route,
    register_route,
    reset_route,
    verify_route,
)
from app.routers.testing.testing_route import router as testing_router

logger = init_logging()

logger.bind(name=None).opt(ansi=True).success(
    f"JourneyLingua is running at <red>{JOURNEY_LINGUA_ENV}</red>"
)
logger.bind(name=None).success(BANNER)


async def request_info(request: Request):
    logger.bind(name=None).debug(f"{request.method} {request.url}")
    try:
        body = await request.json()
        logger.bind(payload=body, name=None).debug("request_json: ")
    except ImportError:
        try:
            body = await request.body()
            if len(body) != 0:
                logger.bind(payload=body, name=None).debug(body)
        except ImportError:
            pass


# [ROUTER]
journeyLingua.include_router(login_route.router)
journeyLingua.include_router(register_route.router)
journeyLingua.include_router(logout_route.router)
journeyLingua.include_router(reset_route.router)
journeyLingua.include_router(verify_route.router)

journeyLingua.include_router(testing_router)


@journeyLingua.get("/", tags=["root"])
def root():
    return {"server": Config.API_TITLE}


@journeyLingua.on_event("startup")
async def startup_event():
    if not await get_redis().ping():
        raise Exception("Connection to redis failed")


@journeyLingua.on_event("shutdown")
async def shutdown_event():
    await get_redis().close()


@journeyLingua.on_event("startup")
async def init_database():
    try:
        logger.bind(name=None).success("Database and tables created success: ✅")
    except Exception as e:
        logger.bind(name=None).error(
            f"Database and tables  created failed: ❌\nError: {e}"
        )
        raise
