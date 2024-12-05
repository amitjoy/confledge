import logging
import uuid
from kink import inject, di
from peewee import Model, CharField, AutoField
from playhouse.db_url import connect
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional

from agent.history.service import HistoryAgent, History
from agent.session.service import SessionAgent, SessionInfo
from config.app import Settings

logger = logging.getLogger(__name__)


class SpacePermission(Model):
    """
    Peewee model representing space permissions.
    """
    id = AutoField()
    user_id = CharField(null=False)
    space_id = CharField(null=False)

    class Meta:
        table_name = di[Settings].db.app_db.permission_table_name
        database = connect(di[Settings].db.app_db.connection_string)


class LoadingResponse(BaseModel):
    """
    Pydantic model representing the loading response.
    """
    sessions: List[SessionInfo] = Field(
        description="The existing chat sessions sorted in descending order of modification or creation date. "
                    "If no existing session exists, a new empty session will be automatically created."
    )
    histories: List[History] = Field(description="History of all the sessions in the same order as sessions")


class LoggedInUserInfo(BaseModel):
    """
    Pydantic model representing logged-in user information.
    """
    user_id: str = Field(description="The user ID of the logged-in user")
    filter: Dict[str, Any] = Field(description="The filter for vector DB")

    class Config:
        arbitrary_types_allowed = True


@inject
class UserAgent:
    """
    Agent for managing user sessions and loading user data.
    """

    def __init__(self, settings: Settings, session_agent: SessionAgent):
        """
        Initializes the UserAgent with the provided settings and session agent.

        :param settings: Application settings.
        :param session_agent: The session agent instance.
        """
        self.settings = settings
        self.session_agent = session_agent

    async def load(self, user_id: str) -> Optional[LoadingResponse]:
        """
        Loads the data for a user.

        :param user_id: The user ID.
        :return: LoadingResponse if successful, None if the user is already logged in.
        """

        def _filter(user_id: str) -> Dict[str, Any]:
            logger.debug(f"Initializing filter for user '{user_id}'")
            permissions = SpacePermission.select().where(SpacePermission.user_id == user_id)
            space_ids = [permission.space_id for permission in permissions]
            return {'space_key': {'$in': space_ids}} if space_ids else {}

        if user_id in di:
            logger.error(f"User ID '{user_id}' is already logged in")
            return None

        logger.info(f"Loading data for user ID '{user_id}'")
        db_filter = _filter(user_id)
        user_info = LoggedInUserInfo(user_id=user_id, filter=db_filter)
        di[user_id] = user_info.model_dump()

        existing_sessions = await self.session_agent.sessions(user_id)
        if not existing_sessions:
            new_session_id = str(uuid.uuid4())
            if await self.session_agent.new_session(user_id=user_id,
                                                    session_id=new_session_id,
                                                    session_name="Default Chat"):
                await self.session_agent.open_session(user_id=user_id, session_id=new_session_id)

        existing_sessions = await self.session_agent.sessions(user_id)
        histories = [
            await HistoryAgent(session_id=session.session_id).history()
            for session in existing_sessions
        ]
        for session in existing_sessions:
            await self.session_agent.open_session(user_id=user_id, session_id=session.session_id)

        return LoadingResponse(sessions=existing_sessions, histories=histories)

    async def login(self, user_id: str) -> bool:
        """
        Logs in the user.

        :param user_id: The user ID.
        :return: True if the user is logged in successfully, False if already logged in.
        """
        if user_id in di:
            logger.info(f"User ID '{user_id}' is already logged in")
            return False

        logger.info(f"User ID '{user_id}' has logged in")
        return True

    async def logout(self, user_id: str) -> bool:
        """
        Logs out the user.

        :param user_id: The user ID.
        :return: True if the user is logged out successfully, False if not logged in.
        """
        if user_id not in di:
            logger.info(f"User ID '{user_id}' is NOT logged in")
            return False

        logger.info(f"User ID '{user_id}' is logging out")
        existing_sessions = await self.session_agent.sessions(user_id)
        for session in existing_sessions:
            self.session_agent.invalidate_session(session.session_id)
        di._services.pop(user_id)
        return True
