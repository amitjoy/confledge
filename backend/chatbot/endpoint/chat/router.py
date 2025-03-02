from http import HTTPStatus

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import StreamingResponse, JSONResponse
from kink import di
from pydantic import BaseModel, Field
from typing import Annotated, Set

from agent.session.service import SessionAgent
from common.auth.basic.auth import verify_credentials
from common.rate_limit import rate_limiter
from endpoint import UUID4_PATTERN

router = APIRouter()


class SourcesResponse(BaseModel):
    """
    Response model for returning sources in a streaming response.
    """
    docs: Set[str] = Field(description="The field in the streaming response containing all sources")


class CompletionResponse(BaseModel):
    """
    Response model for returning completion chunks in a streaming response.
    """
    id: int = Field(description="The ID of the completion response")
    response: str = Field(description="The field in the streaming response containing completion chunk")


@router.get(
    path="/ask",
    name="Chat Endpoint",
    description="The main endpoint to ask a question to the foundation model",
    summary="Endpoint to ask question",
    tags=["chat", "ask", "chat"]
)
@rate_limiter(limit=40, seconds=60)
async def ask(
        request: Request,
        question: str = Annotated[str, Query(title="The question", min_length=1)],
        session_id: str = Annotated[
            str, Query(title="The session ID", min_length=36, max_length=36, pattern=UUID4_PATTERN)],
        user_id: str = Depends(verify_credentials),
        session_agent: SessionAgent = Depends(lambda: di[SessionAgent])
):
    """
    Endpoint to ask a question to the foundation model.

    :param request: The HTTP request object.
    :param question: The question to ask.
    :param session_id: The session ID.
    :param user_id: The user ID.
    :param session_agent: The session agent instance.
    :return: A StreamingResponse with the answer and sources.
    """
    is_owned = await session_agent.check_session_id_ownership(session_id=session_id, user_id=user_id)
    if not is_owned:
        return JSONResponse(
            content=f"Session {session_id} does not belong to {user_id}",
            status_code=HTTPStatus.FORBIDDEN
        )

    chatbot = session_agent.chatbot(session_id)
    if not chatbot:
        return JSONResponse(
            content=f"No session associated with {session_id}",
            status_code=HTTPStatus.NOT_FOUND
        )

    history_agent = chatbot.history_agent
    inputs = {
        "input": question,
        "chat_history": history_agent.retrieve_history_unwrapped()
    }

    def stream_message():
        history = history_agent.retrieve_history()
        ai_message_id = int(history[-1].id) + 2 if history else 2
        for chunk in chatbot.chain.stream(input=inputs, config={"configurable": {"session_id": session_id}}):
            if "context" in chunk:
                sources = chunk["context"]
                src = {source.metadata['source'] for source in sources}
                history_agent.message_history.sources = list(src)
                docs = SourcesResponse(docs=history_agent.message_history.sources)
                yield f"data: {docs.model_dump_json()}\n\n"
            elif "answer" in chunk:
                completion = CompletionResponse(id=ai_message_id, response=chunk["answer"])
                yield f"data: {completion.model_dump_json()}\n\n"

    return StreamingResponse(stream_message(), media_type="text/event-stream")
