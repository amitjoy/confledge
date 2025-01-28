from http import HTTPStatus

from fastapi import APIRouter, Depends, Body, Request
from kink import di
from pydantic import BaseModel, Field
from starlette.responses import JSONResponse
from typing import Annotated, Optional

from agent.history.service import HistoryAgent, Feedback
from agent.session.service import SessionAgent
from common.auth.basic.auth import verify_credentials
from common.rate_limit import rate_limiter
from endpoint import UUID4_PATTERN

router = APIRouter()


class FeedbackRequest(BaseModel):
    """
    Request model for providing feedback on AI messages.
    """
    message_id: int = Field(description="The AI message ID", gt=0)
    session_id: str = Field(description="The session ID", min_length=36, max_length=36, pattern=UUID4_PATTERN)
    feedback: Optional[Feedback] = Field(description="The feedback", default=None)

    class Config:
        str_strip_whitespace = True


class FeedbackResponse(BaseModel):
    """
    Response model for feedback update.
    """
    message_id: int = Field(description="The AI message ID")
    feedback: Optional[str] = Field(description="The feedback", default=None)


@router.post(
    path="/feedback",
    name="Prompt Feedback Endpoint",
    description="The endpoint to update feedback to the prompt completion",
    summary="Feedback",
    tags=["Feedback"]
)
@rate_limiter(limit=30, seconds=60)
async def update_feedback(
        request: Request,
        feedback_request: FeedbackRequest = Annotated[FeedbackRequest, Body(title="The feedback request")],
        user_id: str = Depends(verify_credentials),
        session_agent: SessionAgent = Depends(lambda: di[SessionAgent])
):
    """
    Endpoint to update feedback to the prompt completion.

    :param request: The HTTP request object.
    :param feedback_request: The feedback request model.
    :param user_id: The user ID.
    :param session_agent: The session agent instance.
    :return: A JSONResponse indicating the result of the feedback update.
    """
    is_owned = await session_agent.check_session_id_ownership(session_id=feedback_request.session_id, user_id=user_id)
    if not is_owned:
        return JSONResponse(
            content=f"Session {feedback_request.session_id} does not belong to {user_id}",
            status_code=HTTPStatus.FORBIDDEN
        )

    history_agent = HistoryAgent(session_id=feedback_request.session_id)
    is_updated = await history_agent.provide_feedback(
        message_id=feedback_request.message_id,
        feedback=feedback_request.feedback
    )

    if is_updated:
        return JSONResponse(
            content="Feedback has been successfully sent",
            status_code=HTTPStatus.OK
        )

    return JSONResponse(
        content="Feedback cannot be associated with any existing AI message",
        status_code=HTTPStatus.NOT_FOUND
    )
