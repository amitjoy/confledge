import logging
from datetime import datetime, timedelta
from kink import di, inject
from peewee import Model, CharField, DateTimeField
from playhouse.db_url import connect
from playhouse.shortcuts import model_to_dict
from pydantic import BaseModel, Field
from typing import List, Optional

from agent.chat.service import ChatAgent
from agent.history.service import HistoryAgent
from agent.knowledge_base.service import KnowledgeBaseAgent
from config.app import Settings

logger = logging.getLogger(__name__)


class SessionInfo(BaseModel):
    """
    Pydantic model representing session information.
    """
    session_id: str = Field(description="The session ID")
    session_name: str = Field(description="The session name")
    user_id: str = Field(description="The user ID associated with the session")
    created_at: datetime = Field(description="The date and time when it was created")
    last_modified_at: datetime = Field(description="The date and time when it was last modified")


class SessionModel(Model):
    """
    Peewee model representing a session in the database.
    """
    session_id = CharField(unique=True, null=False, primary_key=True)
    session_name = CharField(null=False)
    user_id = CharField(null=False)
    created_at = DateTimeField(null=False, default=datetime.now)
    last_modified_at = DateTimeField(null=False, default=datetime.now)

    class Meta:
        table_name = di[Settings].db.app_db.session_table_name
        database = connect(di[Settings].db.app_db.connection_string)


@inject
class SessionAgent:
    """
    Agent for managing sessions.
    """

    def __init__(self, settings: Settings):
        """
        Initializes the SessionAgent with the provided settings.

        :param settings: Application settings.
        """
        self.settings = settings

    async def new_session(self, user_id: str, session_id: str, session_name: str) -> bool:
        """
        Creates a new session.

        :param user_id: The user ID associated with the session.
        :param session_id: The session ID.
        :param session_name: The session name.
        :return: True if the session was created successfully, False otherwise.
        """
        if SessionModel.select().where(SessionModel.session_id == session_id).exists():
            logger.info(f"Session ID '{session_id}' already exists in session table")
            return False

        logger.debug(f"Storing session info for '{session_id}' in session table")
        SessionModel.create(session_id=session_id, session_name=session_name, user_id=user_id)
        logger.info(f"Session ID '{session_id}' has been created successfully")
        return True

    async def open_session(self, user_id: str, session_id: str) -> Optional[bool]:
        """
        Opens an existing session.

        :param user_id: The user ID associated with the session.
        :param session_id: The session ID.
        :return: True if the session was opened successfully, False if it already exists, None if not found.
        """
        if not SessionModel.select().where(
                (SessionModel.session_id == session_id) & (SessionModel.user_id == user_id)).exists():
            logger.warning(f"Session ID '{session_id}' does not exist")
            return None

        if session_id in di:
            logger.info(f"Session ID '{session_id}' already exists")
            return False

        kb_agent = KnowledgeBaseAgent(user_id)
        history_agent = HistoryAgent(session_id)
        di[session_id] = ChatAgent(kb_agent, history_agent)
        logger.info(f"Session ID '{session_id}' has been opened successfully")
        return True

    async def rename_session(self, session_id: str, new_session_name: str) -> Optional[bool]:
        """
        Renames an existing session.

        :param session_id: The session ID.
        :param new_session_name: The new session name.
        :return: True if the session was renamed successfully, False if not found, None if the name is the same.
        """
        session = SessionModel.get_or_none(SessionModel.session_id == session_id)
        if not session:
            logger.warning(f"Session ID '{session_id}' has not been found")
            return False

        if session.session_name == new_session_name:
            return None

        session.session_name = new_session_name
        session.last_modified_at = datetime.now()
        session.save()
        logger.info(f"Session ID '{session_id}' has been renamed")
        return True

    def invalidate_session(self, session_id: str) -> bool:
        """
        Invalidates a session.

        :param session_id: The session ID.
        :return: True if the session was invalidated successfully, False otherwise.
        """
        if session_id in di:
            di._services.pop(session_id)
            logger.info(f"Session ID '{session_id}' has been invalidated successfully")
            return True

        logger.warning(f"Session ID '{session_id}' doesn't exist to be invalidated")
        return False

    async def remove_session(self, session_id: str) -> bool:
        """
        Removes a session.

        :param session_id: The session ID.
        :return: True if the session was removed successfully, False otherwise.
        """
        if not self.invalidate_session(session_id):
            return False

        await HistoryAgent(session_id).remove_history()

        logger.debug(f"Removing session info for '{session_id}' from session table")
        session = SessionModel.get_or_none(SessionModel.session_id == session_id)
        if not session:
            logger.warning(f"Session ID '{session_id}' has not been found")
            return False

        session.delete_instance()
        logger.info(f"Session ID '{session_id}' has been removed successfully")
        return True

    def chatbot(self, session_id: str) -> Optional[ChatAgent]:
        """
        Retrieves the chatbot associated with a session.

        :param session_id: The session ID.
        :return: The ChatAgent instance if found, None otherwise.
        """
        if session_id in di:
            return di[session_id]

        logger.warning(f"Session ID '{session_id}' has not been found")
        return None

    async def sessions(self, user_id: str) -> List[SessionInfo]:
        """
        Retrieves all sessions for a user.

        :param user_id: The user ID.
        :return: A list of SessionInfo instances.
        """
        logger.debug(f"Listing sessions for user '{user_id}'")
        sessions = SessionModel.select().where(SessionModel.user_id == user_id).order_by(
            SessionModel.last_modified_at.desc())
        return [SessionInfo(**model_to_dict(session)) for session in sessions]

    async def purge_sessions(self, days: float):
        """
        Purges sessions older than the specified number of days.

        :param days: The number of days.
        """
        logger.debug(f"Purging sessions older than {days} days")
        threshold_date = datetime.now() - timedelta(days=days)
        sessions = SessionModel.select().where(SessionModel.created_at < threshold_date)
        for session in sessions:
            await self.remove_session(session.session_id)

    async def check_session_id_ownership(self, session_id: str, user_id: str) -> bool:
        """
        Checks if a session ID is owned by a user.

        :param session_id: The session ID.
        :param user_id: The user ID.
        :return: True if the session ID is owned by the user, False otherwise.
        """
        return any(session.session_id == session_id for session in await self.sessions(user_id))
