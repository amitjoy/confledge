import logging
from kink import inject
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from agent.healthcheck.model import HealthCheckStatusEnum
from agent.healthcheck.spi import HealthCheckAbstract
from config.app import Settings

logger = logging.getLogger(__name__)


@inject(alias=HealthCheckAbstract)
class HealthCheckAppDB(HealthCheckAbstract):

    def __init__(self, settings: Settings):
        self._tags = ["db"]
        self.settings = settings
        self._service = "hc-app-db"
        super().__init__(service=self._service, tags=self._tags)

    def check_health(self) -> HealthCheckStatusEnum:
        logger.info(f"Executing Healthcheck: {self._service}")
        engine = create_engine(self.settings.db.app_db.connection_string)
        session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        with session() as s:
            try:
                s.execute(text("SELECT 1"))
                return HealthCheckStatusEnum.HEALTHY
            except:
                logger.info(f"Cannot execute Healthcheck: {self._service}")
        return HealthCheckStatusEnum.UNHEALTHY
