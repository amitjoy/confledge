import logging
from datetime import datetime, timedelta
from kink import inject
from typing import List, Optional

from agent.healthcheck.model import HealthCheckModel, HealthCheckEntityModel, HealthCheckStatusEnum
from agent.healthcheck.spi import HealthCheckAbstract

logger = logging.getLogger(__name__)


@inject
class HealthCheckAgent:
    """
    Agent responsible for performing health checks on various services and aggregating the results.
    """

    def __init__(self) -> None:
        self._health_items: List[HealthCheckAbstract] = []
        self._health: Optional[HealthCheckModel] = None
        self._entity_start_time: Optional[datetime] = None
        self._entity_stop_time: Optional[datetime] = None
        self._total_start_time: Optional[datetime] = None
        self._total_stop_time: Optional[datetime] = None

    def add(self, item: HealthCheckAbstract) -> None:
        """
        Adds a health check item to the list of items to be checked.

        :param item: A health check item implementing HealthCheckAbstract.
        """
        self._health_items.append(item)

    def _start_timer(self, entity_timer: bool) -> None:
        """
        Starts the timer for either an individual entity or the total check.

        :param entity_timer: Boolean indicating if the timer is for an entity or the total check.
        """
        if entity_timer:
            self._entity_start_time = datetime.now()
        else:
            self._total_start_time = datetime.now()

    def _stop_timer(self, entity_timer: bool) -> None:
        """
        Stops the timer for either an individual entity or the total check.

        :param entity_timer: Boolean indicating if the timer is for an entity or the total check.
        """
        if entity_timer:
            self._entity_stop_time = datetime.now()
        else:
            self._total_stop_time = datetime.now()

    def _get_time_taken(self, entity_timer: bool) -> timedelta:
        """
        Calculates the time taken for either an individual entity or the total check.

        :param entity_timer: Boolean indicating if the time taken is for an entity or the total check.
        :return: Time taken as a timedelta.
        """
        if entity_timer:
            return self._entity_stop_time - self._entity_start_time
        return self._total_stop_time - self._total_start_time

    def _format_model(self) -> dict:
        """
        Formats the health check model for output, converting enums and timedeltas to strings.

        :return: A dictionary representation of the health check model.
        """

        def format_entity(entity: HealthCheckEntityModel) -> dict:
            entity_dict = entity.model_dump()
            entity_dict["status"] = entity.status.value
            entity_dict["time_taken"] = str(entity.time_taken)
            return entity_dict

        self._health.entities = [format_entity(entity) for entity in self._health.entities]
        self._health.status = self._health.status.value
        self._health.total_time_taken = str(self._health.total_time_taken)

        return self._health.model_dump()

    async def check(self) -> dict:
        """
        Performs health checks on all added health check items and returns the aggregated results.

        :return: A dictionary representing the overall health check status and details.
        """
        self._health = HealthCheckModel()
        self._start_timer(entity_timer=False)

        for item in self._health_items:
            entity = HealthCheckEntityModel(service=item.service, tags=item.tags)
            self._start_timer(entity_timer=True)
            entity.status = item.check_health()
            self._stop_timer(entity_timer=True)
            entity.time_taken = self._get_time_taken(entity_timer=True)

            if entity.status == HealthCheckStatusEnum.UNHEALTHY:
                self._health.status = HealthCheckStatusEnum.UNHEALTHY

            self._health.entities.append(entity)

        self._stop_timer(entity_timer=False)
        self._health.total_time_taken = self._get_time_taken(entity_timer=False)

        return self._format_model()
