from http import HTTPStatus

from fastapi import APIRouter, Depends, Path, Body, Request
from fastapi.responses import JSONResponse
from kink import di
from pydantic import BaseModel, Field
from typing import List, Annotated

from agent.history.service import HistoryAgent
from agent.session.service import SessionAgent, SessionInfo
from common.auth.basic.auth import verify_credentials
from common.rate_limit import rate_limiter
from endpoint import UUID4_PATTERN

router = APIRouter()


class SessionCreateRequest(BaseModel):
    """
    Request model for creating a new session.
    """
    session_name: str = Field(description="The session name", min_length=1)

    class Config:
        str_strip_whitespace = True


class SessionRenameRequest(BaseModel):
    """
    Request model for renaming an existing session.
    """
    new_session_name: str = Field(description="The new session name", min_length=1)

    class Config:
        str_strip_whitespace = True


@router.get(
    path="/sessions/{user_id}",
    name="Chat Session Retrieval Endpoint",
    description="The endpoint to retrieve all the chat sessions initiated by the specified user",
    summary="Chat Sessions Retrieval per User",
    tags=["session"]
)
@rate_limiter(limit=20, seconds=60)
async def retrieve_sessions(
        request: Request,
        user_id: str = Depends(verify_credentials),
        session_agent: SessionAgent = Depends(lambda: di[SessionAgent])
) -> List[SessionInfo]:
    """
    Endpoint to retrieve all chat sessions initiated by the specified user.

    :param request: The HTTP request object.
    :param user_id: The user ID.
    :param session_agent: The session agent instance.
    :return: A list of SessionInfo instances.
    """
    sessions = await session_agent.sessions(user_id)
    return sessions


@router.get(
    path="/sessions/{session_id}/history",
    name="History Retrieval Endpoint",
    description="The endpoint to retrieve all messages in a specific chat session",
    summary="History per Chat Session",
    tags=["session"]
)
@rate_limiter(limit=30, seconds=60)
async def retrieve_history(
        request: Request,
        session_id: Annotated[
            str, Path(title="The unique ID of session", min_length=36, max_length=36, pattern=UUID4_PATTERN)],
        user_id: str = Depends(verify_credentials),
        session_agent: SessionAgent = Depends(lambda: di[SessionAgent])
):
    """
    Endpoint to retrieve all messages in a specific chat session.

    :param request: The HTTP request object.
    :param session_id: The session ID.
    :param user_id: The user ID.
    :param session_agent: The session agent instance.
    :return: A JSONResponse containing the session history.
    """
    is_owned = await session_agent.check_session_id_ownership(session_id=session_id, user_id=user_id)
    if not is_owned:
        return JSONResponse(content=f"Session {session_id} does not belong to {user_id}",
                            status_code=HTTPStatus.FORBIDDEN)

    history_agent = HistoryAgent(session_id=session_id)
    history = await history_agent.history()
    return history


@router.post(
    path="/sessions/{session_id}/invalidate",
    name="Chat Session Invalidation Endpoint",
    description="The endpoint to destroy all expensive resources created for a chat session",
    summary="Chat Session Invalidation",
    tags=["session"]
)
@rate_limiter(limit=10, seconds=60)
async def invalidate_session(
        request: Request,
        session_id: Annotated[
            str, Path(title="The unique ID of session", min_length=36, max_length=36, pattern=UUID4_PATTERN)],
        user_id: str = Depends(verify_credentials),
        session_agent: SessionAgent = Depends(lambda: di[SessionAgent])
):
    """
    Endpoint to invalidate a chat session.

    :param request: The HTTP request object.
    :param session_id: The session ID.
    :param user_id: The user ID.
    :param session_agent: The session agent instance.
    :return: A JSONResponse indicating the result of the invalidation.
    """
    is_owned = await session_agent.check_session_id_ownership(session_id=session_id, user_id=user_id)
    if not is_owned:
        return JSONResponse(content=f"Session {session_id} does not belong to {user_id}",
                            status_code=HTTPStatus.FORBIDDEN)

    is_invalidated = session_agent.invalidate_session(session_id)
    if is_invalidated:
        return JSONResponse(content=f"Session {session_id} has been successfully invalidated",
                            status_code=HTTPStatus.OK)
    return JSONResponse(content=f"Session {session_id} doesn't exist", status_code=HTTPStatus.NOT_FOUND)


@router.post(
    path="/sessions/{session_id}/rename",
    name="Chat Session Rename Endpoint",
    description="The endpoint to rename an existing chat session",
    summary="Chat Session Rename",
    tags=["session"]
)
@rate_limiter(limit=20, seconds=60)
async def rename_session(
        request: Request,
        session_id: Annotated[
            str, Path(title="The unique ID of session", min_length=36, max_length=36, pattern=UUID4_PATTERN)],
        rename_request: SessionRenameRequest = Annotated[SessionRenameRequest, Body(title="The session request")],
        user_id: str = Depends(verify_credentials),
        session_agent: SessionAgent = Depends(lambda: di[SessionAgent])
):
    """
    Endpoint to rename an existing chat session.

    :param request: The HTTP request object.
    :param session_id: The session ID.
    :param rename_request: The rename request model.
    :param user_id: The user ID.
    :param session_agent: The session agent instance.
    :return: A JSONResponse indicating the result of the renaming operation.
    """
    is_owned = await session_agent.check_session_id_ownership(session_id=session_id, user_id=user_id)
    if not is_owned:
        return JSONResponse(content=f"Session {session_id} does not belong to {user_id}",
                            status_code=HTTPStatus.FORBIDDEN)

    is_renamed = await session_agent.rename_session(session_id, rename_request.new_session_name)
    if is_renamed is True:
        return JSONResponse(content=f"Session {session_id} has been successfully renamed", status_code=HTTPStatus.OK)
    if is_renamed is False:
        return JSONResponse(content=f"Session {session_id} doesn't exist", status_code=HTTPStatus.NOT_FOUND)
    return JSONResponse(content=f"Session {session_id} already has the same name", status_code=HTTPStatus.BAD_REQUEST)


@router.put(
    path="/sessions/{session_id}/create",
    name="Chat Session Initiation Endpoint",
    description="The endpoint to create a new chat session",
    summary="Chat Session Initiation",
    tags=["session"]
)
@rate_limiter(limit=20, seconds=60)
async def create_session(
        request: Request,
        session_id: Annotated[
            str, Path(title="The unique ID of session", min_length=36, max_length=36, pattern=UUID4_PATTERN)],
        create_request: SessionCreateRequest = Annotated[SessionCreateRequest, Body(title="The session request")],
        user_id: str = Depends(verify_credentials),
        session_agent: SessionAgent = Depends(lambda: di[SessionAgent])
):
    """
    Endpoint to create a new chat session.

    :param request: The HTTP request object.
    :param session_id: The session ID.
    :param create_request: The create request model.
    :param user_id: The user ID.
    :param session_agent: The session agent instance.
    :return: A JSONResponse indicating the result of the creation operation.
    """
    is_created = await session_agent.new_session(user_id, session_id, create_request.session_name)
    if is_created:
        await session_agent.open_session(user_id, session_id)
        return JSONResponse(content=f"Session {session_id} has been successfully created",
                            status_code=HTTPStatus.CREATED)
    return JSONResponse(content=f"Session {session_id} already exists", status_code=HTTPStatus.BAD_REQUEST)


@router.put(
    path="/sessions/{session_id}/open",
    name="Chat Session Initiation Endpoint",
    description="Endpoint to open an existing chat session",
    summary="Chat Session Initiation",
    tags=["session"]
)
@rate_limiter(limit=20, seconds=60)
async def open_session(
        request: Request,
        session_id: Annotated[
            str, Path(title="The unique ID of session", min_length=36, max_length=36, pattern=UUID4_PATTERN)],
        user_id: str = Depends(verify_credentials),
        session_agent: SessionAgent = Depends(lambda: di[SessionAgent])
) -> JSONResponse:
    """
    Endpoint to open an existing chat session.

    :param request: The HTTP request object.
    :param session_id: The unique ID of the session.
    :param user_id: The user ID.
    :param session_agent: The session agent instance.
    :return: A JSONResponse indicating the result of the operation.
    """
    is_owned = await session_agent.check_session_id_ownership(session_id=session_id, user_id=user_id)
    if not is_owned:
        return JSONResponse(content=f"Session {session_id} does not belong to {user_id}",
                            status_code=HTTPStatus.FORBIDDEN)

    is_opened = await session_agent.open_session(user_id, session_id)
    if is_opened is True:
        return JSONResponse(content=f"Session {session_id} has been successfully opened",
                            status_code=HTTPStatus.CREATED)
    if is_opened is False:
        return JSONResponse(content=f"Session {session_id} already opened", status_code=HTTPStatus.OK)
    return JSONResponse(content=f"Session {session_id} does not exist", status_code=HTTPStatus.NOT_FOUND)


@router.delete(
    path="/sessions/{session_id}/remove",
    name="Chat Session Deletion Endpoint",
    description="Endpoint to delete a chat session",
    summary="Session Deletion",
    tags=["session"]
)
@rate_limiter(limit=20, seconds=60)
async def remove_session(
        request: Request,
        session_id: Annotated[
            str, Path(title="The unique ID of session", min_length=36, max_length=36, pattern=UUID4_PATTERN)],
        user_id: str = Depends(verify_credentials),
        session_agent: SessionAgent = Depends(lambda: di[SessionAgent])
) -> JSONResponse:
    """
    Endpoint to delete a chat session.

    :param request: The HTTP request object.
    :param session_id: The unique ID of the session.
    :param user_id: The user ID.
    :param session_agent: The session agent instance.
    :return: A JSONResponse indicating the result of the operation.
    """
    is_owned = await session_agent.check_session_id_ownership(session_id=session_id, user_id=user_id)
    if not is_owned:
        return JSONResponse(content=f"Session {session_id} does not belong to {user_id}",
                            status_code=HTTPStatus.FORBIDDEN)

    is_removed = await session_agent.remove_session(session_id)
    if is_removed:
        return JSONResponse(content=f"Session {session_id} has been successfully removed", status_code=HTTPStatus.OK)
    return JSONResponse(content=f"Session {session_id} doesn't exist", status_code=HTTPStatus.NOT_FOUND)
