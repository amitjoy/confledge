import logging
import os
import psutil
from kink import inject

from agent.healthcheck.model import HealthCheckStatusEnum
from agent.healthcheck.spi import HealthCheckAbstract

logger = logging.getLogger(__name__)


@inject(alias=HealthCheckAbstract)
class HealthCheckCPU(HealthCheckAbstract):

    def __init__(self):
        self._tags = ["os"]
        self._service = "hc-cpu-usage"
        super().__init__(service=self._service, tags=self._tags)

    def check_health(self) -> HealthCheckStatusEnum:
        logger.info(f"Executing Healthcheck: {self._service}")
        _, _, load = psutil.getloadavg()

        cpu_usage = (load / os.cpu_count()) * 100
        if cpu_usage > 90:
            return HealthCheckStatusEnum.UNHEALTHY
        return HealthCheckStatusEnum.HEALTHY
