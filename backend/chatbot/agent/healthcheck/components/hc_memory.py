import logging
import psutil
from kink import inject

from agent.healthcheck.model import HealthCheckStatusEnum
from agent.healthcheck.spi import HealthCheckAbstract

logger = logging.getLogger(__name__)


@inject(alias=HealthCheckAbstract)
class HealthCheckMemory(HealthCheckAbstract):

    def __init__(self):
        self._tags = ["os"]
        self._service = "hc-memory-usage"
        super().__init__(service=self._service, tags=self._tags)

    def check_health(self) -> HealthCheckStatusEnum:
        logger.info(f"Executing Healthcheck: {self._service}")
        memory_usage = psutil.virtual_memory()[2]
        if memory_usage > 90:
            return HealthCheckStatusEnum.UNHEALTHY
        return HealthCheckStatusEnum.HEALTHY
