from http import HTTPStatus

from fastapi import APIRouter, Depends, Request
from fastapi.encoders import jsonable_encoder
from kink import di
from starlette.responses import JSONResponse
from typing import List, Any

from agent.healthcheck.model import HealthCheckStatusEnum
from agent.healthcheck.service import HealthCheckAgent
from agent.healthcheck.spi import HealthCheckAbstract
from common.rate_limit import rate_limiter

router = APIRouter()


@router.get(
    path='/health',
    name="Health Check Endpoint",
    description="The endpoint to trigger all health checks",
    summary="Health Check Trigger",
    tags=["health", "healthcheck"]
)
@rate_limiter(limit=5, seconds=60)
async def retrieve_jobs(
        request: Request = None,
        hc_agent: HealthCheckAgent = Depends(lambda: di[HealthCheckAgent]),
        hc_components: List[HealthCheckAbstract] = Depends(lambda: di[List[HealthCheckAbstract]])
) -> JSONResponse:
    """
    Endpoint to trigger all health checks.

    :param request: The HTTP request object.
    :param hc_agent: The health check agent instance.
    :param hc_components: A list of health check components.
    :return: A JSONResponse containing the health check results.
    """

    def encode_json(value: Any) -> Any:
        return jsonable_encoder(value or {})

    for component in hc_components:
        hc_agent.add(component)

    response = await hc_agent.check()
    status_code = HTTPStatus.INTERNAL_SERVER_ERROR if response[
                                                          "status"] == HealthCheckStatusEnum.UNHEALTHY else HTTPStatus.OK

    return JSONResponse(content=encode_json(response), status_code=status_code)
