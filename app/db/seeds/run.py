import asyncio
import sys

from loguru import logger

sys.path.append("/app")

from app.db.seeds.seeder import Seeder
from app.core.database import AsyncSessionLocal


async def main():
    async with AsyncSessionLocal() as session:
        seeder = Seeder(session)
        await seeder.seed()


if __name__ == "__main__":
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(main())
    except Exception:
        logger.exception("error occured!!")
        sys.exit(1)
