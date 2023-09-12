from loguru import logger
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.seeds.data.data_protocol import SeedDataProtocol
from app.db.seeds.data.sex import SeedDataSex


class Seeder:
    session: Session
    seed_instances: list[SeedDataProtocol]

    def __init__(self, session: Session) -> None:
        self.session = session
        self.seed_instances = [SeedDataSex()]

    async def seed(self):
        logger.info("import seeds...")
        try:
            self.session.begin()
            for seed_instance in self.seed_instances:
                await self._truncate_table(seed_instance.table_name())
                self.session.add_all(seed_instance.data())
            await self.session.commit()
            logger.info("import seeds completed.")
        except Exception:
            await self.session.rollback()
            logger.exception("faild to import seeds!!")

    async def _truncate_table(self, table_name: str) -> None:
        logger.info(f"truncate table: {table_name}")
        await self.session.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
        await self.session.execute(text(f"TRUNCATE {table_name}"))
        await self.session.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
