import logging
from google.oauth2.service_account import Credentials
from kink import inject

from config.app import Settings

logger = logging.getLogger(__name__)


@inject
class GCPAuth:
    """
    Handles Google Cloud Platform authentication using service account credentials.
    """

    def __init__(self, settings: Settings):
        """
        Initializes the GCPAuth class with the provided settings.

        :param settings: Settings object containing GCP configuration.
        """
        self.settings = settings
        logger.info("Initializing GCP service account authentication credentials")

    def has_service_account(self) -> bool:
        """
        Checks if the service account path is configured.

        :return: True if the service account path is non-empty, False otherwise.
        """
        service_account_path = self.settings.gcp.vertex.service_account_path.strip()
        return bool(service_account_path)

    @property
    def credentials(self) -> Credentials:
        """
        Retrieves the GCP service account credentials.

        :return: Credentials object for the service account.
        """
        return Credentials.from_service_account_file(self.settings.gcp.vertex.service_account_path)

    @property
    def service_account_file(self) -> str:
        """
        Returns the path to the service account file.

        :return: Path to the service account file as a string.
        """
        return self.settings.gcp.vertex.service_account_path
