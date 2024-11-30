import logging
from datetime import timedelta
from enum import auto, StrEnum
from pydantic import BaseModel
from typing import List, Optional

logger = logging.getLogger(__name__)


class HealthCheckStatusEnum(StrEnum):
    """
    Enumeration for Health Check Status.
    """
    HEALTHY = auto()
    UNHEALTHY = auto()


class HealthCheckEntityModel(BaseModel):
    """
    Model representing the health check status of an individual service.
    """
    service: str
    status: HealthCheckStatusEnum = HealthCheckStatusEnum.HEALTHY
    time_taken: Optional[timedelta] = None
    tags: List[str] = []


class HealthCheckModel(BaseModel):
    """
    Model representing the overall health check status.
    """
    status: HealthCheckStatusEnum = HealthCheckStatusEnum.HEALTHY
    total_time_taken: Optional[timedelta] = None
    entities: List[HealthCheckEntityModel] = []
