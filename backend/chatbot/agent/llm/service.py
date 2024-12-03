import logging
from kink import inject
from langchain_core.language_models import BaseLanguageModel
from langchain_google_vertexai import ChatVertexAI, VertexAI

from agent.auth.service import GCPAuth
from config.app import Settings

logger = logging.getLogger(__name__)


@inject(use_factory=True)
class ChatVertexLLM:
    """
    Class for initializing and providing access to the Vertex AI chat language model.
    """

    def __init__(self, settings: Settings, gcp_auth: GCPAuth):
        """
        Initializes the ChatVertexLLM with the provided settings and GCP authentication.

        :param settings: Application settings.
        :param gcp_auth: GCP authentication service.
        """
        logger.debug("Initializing Vertex AI chat language model")
        credentials = gcp_auth.credentials if gcp_auth.has_service_account() else None
        self._model = ChatVertexAI(
            credentials=credentials,
            top_p=settings.gcp.vertex.model.top_p,
            top_k=settings.gcp.vertex.model.top_k,
            model_name=settings.gcp.vertex.model.name,
            verbose=settings.gcp.vertex.model.verbose,
            streaming=settings.gcp.vertex.model.streaming,
            temperature=settings.gcp.vertex.model.temperature,
            max_output_tokens=settings.gcp.vertex.model.max_output_tokens
        )

    @property
    def model(self) -> BaseLanguageModel:
        """
        Returns the Vertex AI chat language model.

        :return: BaseLanguageModel instance.
        """
        return self._model


@inject(use_factory=True)
class VertexLLM:
    """
    Class for initializing and providing access to the Vertex AI language model.
    """

    def __init__(self, settings: Settings, gcp_auth: GCPAuth):
        """
        Initializes the VertexLLM with the provided settings and GCP authentication.

        :param settings: Application settings.
        :param gcp_auth: GCP authentication service.
        """
        logger.debug("Initializing Vertex AI language model")
        credentials = gcp_auth.credentials if gcp_auth.has_service_account() else None
        self._model = VertexAI(
            credentials=credentials,
            top_p=settings.gcp.vertex.model.top_p,
            top_k=settings.gcp.vertex.model.top_k,
            model_name=settings.gcp.vertex.model.name,
            verbose=settings.gcp.vertex.model.verbose,
            streaming=False,
            temperature=settings.gcp.vertex.model.temperature,
            max_output_tokens=settings.gcp.vertex.model.max_output_tokens
        )

    @property
    def model(self) -> BaseLanguageModel:
        """
        Returns the Vertex AI language model.

        :return: BaseLanguageModel instance.
        """
        return self._model
