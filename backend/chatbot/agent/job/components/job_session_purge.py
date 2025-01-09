import logging
from kink import inject

from agent.job.spi import JobAbstract, JobType
from agent.session.service import SessionAgent

logger = logging.getLogger(__name__)


@inject(alias=JobAbstract)
class JobSessionPurge(JobAbstract):
    """
    Job for purging old sessions.
    """

    def __init__(self, session_agent: SessionAgent):
        """
        Initializes the JobSessionPurge with the given session agent.

        :param session_agent: The SessionAgent instance to manage sessions.
        """
        super().__init__(job_type=JobType.SESSION_PURGE)
        self.session_agent = session_agent

    def perform(self, **kwargs):
        """
        Executes the session purge job.

        :param kwargs: Additional keyword arguments for job execution.
        """
        logger.info("Executing Session Purge Job")
        try:
            days: float = kwargs.get("days", 30)
            self.session_agent.purge_sessions(days)
            logger.info("Session purge job executed successfully")
        except Exception as e:
            logger.exception("Session purge job failed", exc_info=e)
