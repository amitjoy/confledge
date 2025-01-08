import logging
from kink import inject
from langchain_community.vectorstores.pgvector import PGVector

from agent.healthcheck.model import HealthCheckStatusEnum
from agent.healthcheck.spi import HealthCheckAbstract
from agent.knowledge_base.service import VectorDB
from config.app import Settings

logger = logging.getLogger(__name__)


@inject(alias=HealthCheckAbstract)
class HealthCheckVectorDB(HealthCheckAbstract):

    def __init__(self, vector_db: VectorDB, settings: Settings):
        self._tags = ["db"]
        self.vector_db = vector_db
        self.settings = settings
        self._service = "hc-vector-db"
        super().__init__(service=self._service, tags=self._tags)

    def check_health(self) -> HealthCheckStatusEnum:
        logger.info(f"Executing Healthcheck: {self._service}")
        try:
            db: PGVector = self.vector_db.db
            db.search(query="test", search_type=self.settings.db.vector_db.retriever.type)
            return HealthCheckStatusEnum.HEALTHY
        except:
            logger.info(f"Cannot execute Healthcheck: {self._service}")
        return HealthCheckStatusEnum.UNHEALTHY
