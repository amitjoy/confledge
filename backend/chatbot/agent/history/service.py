import json
import logging
from enum import Enum, auto, StrEnum
from langchain_core.messages import BaseMessage, HumanMessage
from pydantic import Field, BaseModel
from typing import List, Optional

from agent.history.sql import SQLMessageHistory

logger = logging.getLogger(__name__)


class Feedback(StrEnum):
    """
    Enum for feedback types.
    """
    POSITIVE = auto()
    NEGATIVE = auto()


class Answer(BaseModel):
    """
    Model representing an answer in a QA pair.
    """
    id: int = Field(description="The message ID")
    content: str = Field(description="The message content")
    feedback: Optional[Feedback] = Field(description="Feedback on the message", default=None)
    sources: List[str] = Field(description="The document sources")


class Question(BaseModel):
    """
    Model representing a question in a QA pair.
    """
    content: str = Field(description="The message content")


class QA(BaseModel):
    """
    Model representing a Question-Answer pair.
    """
    question: Question = Field(description="The question")
    answer: Answer = Field(description="The answer")


class History(BaseModel):
    """
    Model representing the message history.
    """
    messages: List[QA] = Field(description="The list of all messages in order")


class MessageActor(str, Enum):
    """
    Enum for message actors.
    """
    HUMAN = "HUMAN"
    AI = "AI"


class Message(BaseModel):
    """
    Model representing a single message.
    """
    id: int = Field(description="The message ID")
    content: str = Field(description="The message content")
    actor: MessageActor = Field(description="The actor who sent the message")


class HistoryAgent:
    """
    Agent responsible for managing message history.
    """

    def __init__(self, session_id: str):
        """
        Initializes the HistoryAgent with a session ID.

        :param session_id: The session ID for tracking the history.
        """
        self.session_id = session_id
        self.message_history = SQLMessageHistory(session_id)

    async def remove_history(self) -> None:
        """
        Removes the message history for the current session.
        """
        logger.debug(f"Removing history for '{self.session_id}'")
        await self.message_history.aclear()

    def retrieve_history(self) -> List[Message]:
        """
        Retrieves the wrapped message history for the current session.

        :return: A list of wrapped messages.
        """
        logger.debug(f"Retrieving history for '{self.session_id}'")
        return [self._wrap_message(m) for m in self.message_history.messages]

    def retrieve_history_unwrapped(self) -> List[BaseMessage]:
        """
        Retrieves the unwrapped message history for the current session.

        :return: A list of base messages.
        """
        logger.debug(f"Retrieving history for '{self.session_id}'")
        return self.message_history.messages

    def add_user_message(self, message: str) -> None:
        """
        Adds a user message to the history.

        :param message: The user message content.
        """
        self.message_history.add_user_message(message)

    def add_ai_message(self, message: str) -> None:
        """
        Adds an AI message to the history.

        :param message: The AI message content.
        """
        self.message_history.add_ai_message(message)

    @staticmethod
    def _wrap_message(message: BaseMessage) -> Message:
        """
        Wraps a base message into a Message model.

        :param message: The base message to wrap.
        :return: A wrapped Message model.
        """
        actor = MessageActor.HUMAN if isinstance(message, HumanMessage) else MessageActor.AI
        return Message(id=message.id, content=message.content, actor=actor)

    @property
    def memory(self) -> SQLMessageHistory:
        """
        Returns the message history.

        :return: An instance of SQLMessageHistory.
        """
        return self.message_history

    async def history(self) -> History:
        """
        Retrieves the detailed history for the current session.

        :return: A History model containing all QA pairs.
        """
        logger.debug(f"Retrieving detailed history for '{self.session_id}'")
        history = self.message_history.messages_wrapped()
        messages = []

        for human_message, ai_message in history:
            human_message_dict = json.loads(human_message.message)
            ai_message_dict = json.loads(ai_message.message)
            sources = json.loads(ai_message.sources) if ai_message.sources else []

            llm_message = Answer(
                id=ai_message.id,
                content=ai_message_dict['data']['content'],
                feedback=ai_message.feedback,
                sources=sources
            )
            user_message = Question(content=human_message_dict["data"]['content'])
            qa_pair = QA(question=user_message, answer=llm_message)
            messages.append(qa_pair)

        return History(messages=messages)

    async def provide_feedback(self, message_id: int, feedback: Optional[Feedback]) -> bool:
        """
        Provides feedback for a specific message.

        :param message_id: The ID of the message to provide feedback for.
        :param feedback: The feedback to provide.
        :return: True if feedback was successfully provided, False otherwise.
        """
        messages = self.retrieve_history()
        message = next((msg for msg in messages if msg.id == message_id), None)

        if not message or message.actor == MessageActor.HUMAN:
            return False

        feedback_str = feedback.value.lower() if feedback else None
        return await self.message_history.update_feedback(
            message_id=message_id,
            session_id=self.session_id,
            feedback=feedback_str
        )
