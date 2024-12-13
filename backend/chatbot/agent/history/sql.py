import json
import logging
from benedict import benedict
from kink import di
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage, messages_from_dict, message_to_dict
from peewee import Model, CharField, AutoField, TextField
from playhouse.db_url import connect
from playhouse.shortcuts import model_to_dict
from traceloop.sdk import Traceloop
from typing import List, Optional

from config.app import Settings

logger = logging.getLogger(__name__)


class HistoryMessageModel(Model):
    """
    Peewee model representing a message in the chat history.
    """
    id = AutoField()
    session_id = CharField(null=False)
    message = TextField(null=False)
    feedback = CharField(null=True)
    sources = TextField(null=True)

    class Meta:
        table_name = di[Settings].db.app_db.history_table_name
        database = connect(di[Settings].db.app_db.connection_string)


class SQLMessageHistory(BaseChatMessageHistory):
    """
    Class for handling SQL-based message history.
    """

    def __init__(self, session_id: str):
        """
        Initializes the SQLMessageHistory with a session ID.

        :param session_id: The session ID for which to manage history.
        """
        self.session_id = session_id
        self.sources = []

    @property
    def messages(self) -> List[BaseMessage]:
        """
        Retrieves all messages for the current session.

        :return: A list of BaseMessage instances.
        """
        messages = HistoryMessageModel.select().where(
            HistoryMessageModel.session_id == self.session_id).order_by(
            HistoryMessageModel.id.asc())
        message_dicts = [json.loads(model_to_dict(row)["message"]) for row in messages]
        return messages_from_dict(message_dicts)

    def messages_wrapped(self):
        """
        Retrieves all messages for the current session in a paired format.

        :return: An iterable of paired messages.
        """
        messages = HistoryMessageModel.select().where(
            HistoryMessageModel.session_id == self.session_id).order_by(
            HistoryMessageModel.id.asc())
        return self._pairwise(messages)

    def add_message(self, message: BaseMessage):
        """
        Adds a message to the history.

        :param message: The message to add.
        """
        msg_dict = message_to_dict(message)
        model = HistoryMessageModel.create(session_id=self.session_id,
                                           message=json.dumps(msg_dict))
        deep_copy_source = benedict(msg_dict)
        update = {'data': {'id': model.id}}
        deep_copy_source.merge(update)
        model.message = json.dumps(deep_copy_source)
        if msg_dict['type'] == 'ai':
            model.sources = json.dumps(self.sources)
        model.save()

    async def update_feedback(self, message_id: int, session_id: str, feedback: Optional[str]) -> bool:
        """
        Updates the feedback for a specific message.

        :param message_id: The ID of the message to update.
        :param session_id: The session ID.
        :param feedback: The feedback to apply.
        :return: True if the feedback was updated, False otherwise.
        """
        messages = HistoryMessageModel.select().where(
            (HistoryMessageModel.session_id == session_id) & (HistoryMessageModel.id == message_id))
        if not messages.exists():
            logger.warning("No associated message found")
            return False

        score = 1 if feedback == "positive" else -1 if feedback == "negative" else 0
        Traceloop.report_score(association_property_name="chat_id",
                               association_property_id=str(message_id),
                               score=score)

        for message in messages:
            message.feedback = feedback
            message.save()
            return True
        return False

    def update_sources(self, message_id: str, session_id: str, sources: List[str]):
        """
        Updates the sources for a specific message.

        :param message_id: The ID of the message to update.
        :param session_id: The session ID.
        :param sources: The sources to update.
        """
        messages = HistoryMessageModel.select().where(
            (HistoryMessageModel.session_id == session_id) & (HistoryMessageModel.id == int(message_id)))
        for message in messages:
            if sources:
                logger.debug(f"Adding sources to existing message with ID: '{message_id}'")
                message.sources = json.dumps(sources)
                message.save()

    def clear(self):
        """
        Clears all messages for the current session.
        """
        messages = HistoryMessageModel.select().where(HistoryMessageModel.session_id == self.session_id)
        for message in messages:
            message.delete_instance()

    @staticmethod
    def _pairwise(iterable):
        """
        Generates pairs of items from the iterable.

        :param iterable: An iterable of items.
        :return: An iterable of paired items.
        """
        a = iter(iterable)
        return zip(a, a)
