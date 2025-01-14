from http import HTTPStatus

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from kink import di

from agent.user.service import UserAgent, LoadingResponse
from common.auth.basic.auth import verify_credentials
from common.rate_limit import rate_limiter

router = APIRouter()


@router.post(
    path="/login",
    name="Telly Login Endpoint",
    description="Endpoint to login.",
    summary="Telly Login",
    tags=["login"]
)
@rate_limiter(limit=15, seconds=60)
async def login(
        request: Request,
        user_id: str = Depends(verify_credentials),
        user_agent: UserAgent = Depends(lambda: di[UserAgent])
) -> JSONResponse:
    """
    Endpoint to handle user login.

    :param request: The HTTP request object.
    :param user_id: The user ID.
    :param user_agent: The user agent instance.
    :return: A JSONResponse indicating the result of the login operation.
    """
    logged_in = await user_agent.login(user_id)
    if not logged_in:
        return JSONResponse(
            content=f"User session of {user_id} cannot be logged in again as it already is elsewhere",
            status_code=HTTPStatus.BAD_REQUEST
        )
    return JSONResponse(
        content=f"User session of {user_id} has successfully been logged in",
        status_code=HTTPStatus.OK
    )


@router.post(
    path="/logout",
    name="Telly Logout Endpoint",
    description="Endpoint to logout from a user session.",
    summary="Telly Logout",
    tags=["logout"]
)
@rate_limiter(limit=15, seconds=60)
async def logout(
        request: Request,
        user_id: str = Depends(verify_credentials),
        user_agent: UserAgent = Depends(lambda: di[UserAgent])
) -> JSONResponse:
    """
    Endpoint to handle user logout.

    :param request: The HTTP request object.
    :param user_id: The user ID.
    :param user_agent: The user agent instance.
    :return: A JSONResponse indicating the result of the logout operation.
    """
    is_logged_out = await user_agent.logout(user_id)
    if not is_logged_out:
        return JSONResponse(
            content=f"User session of {user_id} cannot be logged out as it doesn't exist",
            status_code=HTTPStatus.BAD_REQUEST
        )
    return JSONResponse(
        content=f"User session of {user_id} has successfully been logged out",
        status_code=HTTPStatus.OK
    )


@router.get(
    path="/load",
    name="Telly Data Loading Endpoint",
    description="Endpoint to load existing chat sessions if they exist, otherwise create a new one.",
    summary="Telly Data Loading",
    tags=["load"]
)
@rate_limiter(limit=20, seconds=60)
async def load(
        request: Request,
        user_id: str = Depends(verify_credentials),
        user_agent: UserAgent = Depends(lambda: di[UserAgent])
):
    """
    Endpoint to load existing chat sessions or create a new one.

    :param request: The HTTP request object.
    :param user_id: The user ID.
    :param user_agent: The user agent instance.
    :return: A JSONResponse containing the loading response.
    """
    load_response: LoadingResponse = await user_agent.load(user_id)
    if not load_response:
        return JSONResponse(
            content=f"User {user_id} has already been logged in elsewhere",
            status_code=HTTPStatus.BAD_REQUEST
        )
    return load_response
