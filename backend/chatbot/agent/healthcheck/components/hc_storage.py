import logging
import shutil
from kink import inject

from agent.healthcheck.model import HealthCheckStatusEnum
from agent.healthcheck.spi import HealthCheckAbstract
from config.app import Settings

logger = logging.getLogger(__name__)


@inject(alias=HealthCheckAbstract)
class HealthCheckStorage(HealthCheckAbstract):
    KB = 1024
    MB = 1024 * KB

    def __init__(self, settings: Settings):
        self._tags = ["os"]
        self.settings = settings
        self._service = "hc-storage-usage"
        super().__init__(service=self._service, tags=self._tags)

    def check_health(self) -> HealthCheckStatusEnum:
        logger.info(f"Executing Healthcheck: {self._service}")
        stat = shutil.disk_usage(self.settings.mount_point)
        free_space_in_mb = stat.free / self.MB
        if free_space_in_mb <= 500:
            return HealthCheckStatusEnum.UNHEALTHY
        return HealthCheckStatusEnum.HEALTHY
