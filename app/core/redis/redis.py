import redis.asyncio

from app.config.config import Config

redis_connection = redis.asyncio.from_url(
    f"redis://{Config.REDIS_HOST}:{Config.REDIS_PORT}",
    decode_responses=True,
)


def get_redis():
    """
    @brief Get the redis connection.
    @return a : class : ` ~redis.
    Connection ` or : data : ` None ` if there is no
    """
    return redis_connection
