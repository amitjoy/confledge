from abc import ABC, abstractmethod
from enum import Enum, auto


class JobType(str, Enum):
    """
    Enum representing different types of jobs.
    """
    SESSION_PURGE = auto()


class JobAbstract(ABC):
    """
    Abstract base class for defining a job.
    """

    def __init__(self, job_type: JobType):
        """
        Initializes the JobAbstract with a specific job type.

        :param job_type: The type of job.
        """
        self._job_type = job_type

    @abstractmethod
    def perform(self, **kwargs):
        """
        Abstract method to perform the job. Must be implemented by subclasses.

        :param kwargs: Additional keyword arguments for job execution.
        """
        pass

    @property
    def type(self) -> JobType:
        """
        Returns the type of job.

        :return: The job type.
        """
        return self._job_type
