from abc import ABC, abstractmethod
from typing import Optional, List

from agent.healthcheck.model import HealthCheckStatusEnum


class HealthCheckAbstract(ABC):
    """
    Abstract base class for health checks, defining the structure for health check implementations.
    """

    def __init__(self, service: Optional[str] = None, tags: Optional[List[str]] = None):
        """
        Initializes the HealthCheckAbstract class with a service name and optional tags.

        :param service: The name of the service to be checked.
        :param tags: A list of tags associated with the service.
        """
        self._service = service
        self._tags = tags or []

    @abstractmethod
    def check_health(self) -> HealthCheckStatusEnum:
        """
        Abstract method to request data from the endpoint to validate health.
        Implementations must override this method.

        :return: The health status of the service.
        """
        pass

    @property
    def service(self) -> str:
        """
        Returns the name of the service.

        :return: The service name as a string.
        """
        return self._service

    @property
    def tags(self) -> List[str]:
        """
        Returns the tags associated with the service.
        If no tags are provided, returns a list containing the service name if available.

        :return: A list of tags.
        """
        return self._tags if self._tags else [self._service] if self._service else []
