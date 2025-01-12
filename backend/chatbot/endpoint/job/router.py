from http import HTTPStatus

from apscheduler.jobstores.base import JobLookupError
from datetime import datetime
from fastapi import APIRouter, Body, Path, Depends, Request
from kink import di
from pydantic import BaseModel, Field
from starlette.responses import JSONResponse
from typing import Annotated, List, Any

from agent.job.service import JobAgent, ScheduledJob
from agent.job.spi import JobType
from common.rate_limit import rate_limiter
from endpoint import UUID4_PATTERN

router = APIRouter()


class JobRequest(BaseModel):
    """
    Request model for creating a new job.
    """
    job_name: str = Field(description="The job name", min_length=1)
    job_type: JobType = Field(description="The job type")
    next_run_time: datetime = Field(description="The next job execution time")
    job_config: dict[str, Any] = Field(description="Any configuration required to run the job", default={})

    class Config:
        str_strip_whitespace = True


@router.get(
    path="/jobs",
    name="Job Retrieval Endpoint",
    description="The endpoint to retrieve all the scheduled jobs",
    summary="Job Retrieval",
    tags=["Job"]
)
@rate_limiter(limit=15, seconds=60)
async def retrieve_jobs(
        request: Request = None,
        job_agent: JobAgent = Depends(lambda: di[JobAgent])
) -> List[ScheduledJob]:
    """
    Endpoint to retrieve all the scheduled jobs.

    :param request: The HTTP request object.
    :param job_agent: The job agent instance.
    :return: A list of ScheduledJob instances.
    """
    jobs = await job_agent.list_jobs()
    return jobs


@router.put(
    path="/jobs",
    name="Job Creation Endpoint",
    description="The endpoint to create a new job",
    summary="Job Creation",
    tags=["Job"]
)
@rate_limiter(limit=10, seconds=60)
async def add_job(
        request: Request,
        job_request: JobRequest = Annotated[JobRequest, Body(title="The job request")],
        job_agent: JobAgent = Depends(lambda: di[JobAgent])
) -> str:
    """
    Endpoint to create a new job.

    :param request: The HTTP request object.
    :param job_request: The job request model.
    :param job_agent: The job agent instance.
    :return: The ID of the created job.
    """
    return job_agent.add_job(
        name=job_request.job_name,
        job_type=job_request.job_type,
        next_run_time=job_request.next_run_time,
        config=job_request.job_config
    )


@router.delete(
    path="/jobs/{job_id}",
    name="Job Removal Endpoint",
    description="The endpoint to remove a scheduled job",
    summary="Job Removal",
    tags=["Job"]
)
@rate_limiter(limit=10, seconds=60)
async def remove_job(
        request: Request,
        job_id: Annotated[str, Path(title="The job ID", min_length=36, max_length=36, pattern=UUID4_PATTERN)],
        job_agent: JobAgent = Depends(lambda: di[JobAgent])
):
    """
    Endpoint to remove a scheduled job.

    :param request: The HTTP request object.
    :param job_id: The ID of the job to be removed.
    :param job_agent: The job agent instance.
    :return: A JSONResponse indicating the result of the removal operation.
    """
    try:
        job_agent.remove_job(job_id)
        return JSONResponse(
            content=f"Job {job_id} has been successfully removed",
            status_code=HTTPStatus.OK
        )
    except JobLookupError:
        return JSONResponse(
            content=f"Job {job_id} doesn't exist",
            status_code=HTTPStatus.NOT_FOUND
        )
