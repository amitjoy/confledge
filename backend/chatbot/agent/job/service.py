import uuid
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.job import Job
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from enum import auto, StrEnum
from kink import inject
from pydantic import BaseModel, Field
from pytz import timezone
from typing import List, Any, Dict

from agent.job.spi import JobType, JobAbstract
from config.app import Settings


class JobStatus(StrEnum):
    """
    Enum representing the status of a job.
    """
    SCHEDULED = auto()
    PENDING = auto()


class ScheduledJob(BaseModel):
    """
    Model representing a scheduled job.
    """
    id: str = Field(description="The job ID")
    name: str = Field(description="The job name")
    status: JobStatus = Field(description="The job status")
    next_run_time: datetime = Field(description="The next scheduled time of the job")


@inject
class JobScheduler:
    """
    Scheduler for managing jobs.
    """

    def __init__(self, settings: Settings):
        """
        Initializes the JobScheduler with the given settings.

        :param settings: Application settings.
        """
        jobstores = {
            'default': SQLAlchemyJobStore(
                url=settings.db.app_db.connection_string,
                tablename=settings.db.app_db.job_table_name
            )
        }
        executors = {
            'default': ThreadPoolExecutor(10)
        }
        job_defaults = {
            'max_instances': 3
        }
        self._scheduler = BackgroundScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults,
            timezone=timezone("Europe/Berlin")
        )
        self._scheduler.start()

    @property
    def scheduler(self) -> BackgroundScheduler:
        """
        Returns the scheduler instance.

        :return: BackgroundScheduler instance.
        """
        return self._scheduler


@inject
class JobAgent:
    """
    Agent responsible for managing jobs within the scheduler.
    """

    def __init__(self, settings: Settings, job_scheduler: JobScheduler, components: List[JobAbstract]):
        """
        Initializes the JobAgent with the given settings, scheduler, and job components.

        :param settings: Application settings.
        :param job_scheduler: JobScheduler instance.
        :param components: List of job components implementing JobAbstract.
        """
        self.settings = settings
        self.job_scheduler = job_scheduler
        self.components = components

    def add_job(self, name: str, job_type: JobType, next_run_time: datetime, config: Dict[str, Any]) -> str:
        """
        Adds a new job to the scheduler.

        :param name: The name of the job.
        :param job_type: The type of job to be scheduled.
        :param next_run_time: The next scheduled run time for the job.
        :param config: Configuration dictionary for the job.
        :return: The ID of the scheduled job.
        """
        job_id = str(uuid.uuid4())
        func = next((j.perform for j in self.components if j.job_type == job_type), None)
        if func is None:
            raise ValueError(f"No job component found for job type: {job_type}")

        self.job_scheduler.scheduler.add_job(
            func=func,
            id=job_id,
            name=name,
            kwargs=config,
            next_run_time=next_run_time
        )
        return job_id

    def remove_job(self, job_id: str) -> None:
        """
        Removes a job from the scheduler.

        :param job_id: The ID of the job to be removed.
        """
        self.job_scheduler.scheduler.remove_job(job_id)

    async def list_jobs(self) -> List[ScheduledJob]:
        """
        Lists all scheduled jobs.

        :return: A list of ScheduledJob instances.
        """
        jobs = self.job_scheduler.scheduler.get_jobs()
        return [self._wrap_job(job) for job in jobs]

    def _wrap_job(self, job: Job) -> ScheduledJob:
        """
        Wraps a job into a ScheduledJob model.

        :param job: The job to be wrapped.
        :return: A ScheduledJob instance.
        """
        status = JobStatus.PENDING if job.pending else JobStatus.SCHEDULED
        return ScheduledJob(
            id=job.id,
            name=job.name,
            status=status,
            next_run_time=job.next_run_time
        )
