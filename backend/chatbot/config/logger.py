import logging
import uvicorn
from fastapi_cloud_logging import FastAPILoggingHandler
from google.cloud.logging import Client
from google.cloud.logging_v2.handlers import setup_logging
from kink import inject
from rich.logging import RichHandler

from agent.auth.service import GCPAuth
from config.app import Settings


@inject
class TellyLogging:
    """
    Configures logging for the application using Google Cloud and Rich logging.
    """

    def __init__(self, settings: Settings, gcp_auth: GCPAuth):
        """
        Initializes the TellyLogging with the provided settings and GCP authentication.

        :param settings: Application settings.
        :param gcp_auth: GCP authentication service.
        """
        self.loglevel = logging._nameToLevel[settings.log_level.upper()]
        credentials = gcp_auth.credentials if gcp_auth.has_service_account() else None
        self.client = Client(project=settings.gcp.project_id, credentials=credentials)
        self._handler = FastAPILoggingHandler(
            client=self.client,
            structured=True,
            traceback_length=0,
            name=settings.gcp.logger_name
        )
        self._handler.setLevel(self.loglevel)
        self.log_config = self._initialize_log_config()

    def _initialize_log_config(self) -> dict:
        """
        Initializes the logging configuration for FastAPI.

        :return: A dictionary containing the logging configuration.
        """
        log_config = uvicorn.config.LOGGING_CONFIG
        formatter = "%(asctime)s - %(levelname)s - %(message)s"
        log_config["formatters"]["access"]["fmt"] = formatter
        log_config["formatters"]["default"]["fmt"] = formatter
        return log_config

    def init(self):
        """
        Sets up the logging configuration for the application.
        """
        logging.basicConfig(
            level=self.loglevel,
            format="%(message)s",
            datefmt="[%X]",
            handlers=[RichHandler(rich_tracebacks=True)]
        )
        setup_logging(self._handler)

    @property
    def handler(self) -> FastAPILoggingHandler:
        """
        Returns the FastAPI logging handler.

        :return: The FastAPI logging handler.
        """
        return self._handler

    @property
    def fastapi_log_config(self) -> dict:
        """
        Returns the logging configuration for FastAPI.

        :return: A dictionary containing the FastAPI logging configuration.
        """
        return self.log_config
