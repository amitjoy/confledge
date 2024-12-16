import logging
from kink import di, inject
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor
from langchain_core.retrievers import BaseRetriever
from langchain_google_vertexai import VertexAIEmbeddings
from langchain_postgres import PGVector
from typing import Any, Dict

from agent.auth.service import GCPAuth
from agent.llm.service import VertexLLM
from config.app import Settings

logger = logging.getLogger(__name__)


class KnowledgeBaseAgent:
    """
    Agent for managing knowledge base retrieval.
    """

    def __init__(self, user_id: str):
        """
        Initializes the KnowledgeBaseAgent with the specified user ID.

        :param user_id: The ID of the user.
        """
        settings: Settings = di[Settings]
        vector_db: VectorDB = di[VectorDB]
        user: Dict[str, Any] = di[user_id]

        logger.debug(f"Initializing vector DB retriever for user '{user_id}'")
        vertex: VertexLLM = di[VertexLLM]
        compressor = LLMChainExtractor.from_llm(llm=vertex.model)

        self.db_retriever = vector_db.db.as_retriever(
            search_type=settings.db.vector_db.retriever.type,
            search_kwargs={
                "k": settings.db.vector_db.retriever.k,
                "filter": user['filter']
            }
        )

        '''Contextual compression is disabled since according to experience, it removes 
        important information from the context. Keeping it for future use.'''
        self._retriever = ContextualCompressionRetriever(
            base_compressor=compressor,
            base_retriever=self.db_retriever
        )

    @property
    def retriever(self) -> BaseRetriever:
        """
        Returns the base retriever for the knowledge base.

        :return: BaseRetriever instance.
        """
        return self.db_retriever


@inject
class VectorDB:
    """
    Class for managing the vector database and embeddings.
    """

    def __init__(self, settings: Settings, gcp_auth: GCPAuth):
        """
        Initializes the VectorDB with the specified settings and GCP authentication.

        :param settings: Application settings.
        :param gcp_auth: GCP authentication service.
        """
        logger.info("Initializing Vertex AI embeddings")
        self._embedding = VertexAIEmbeddings(
            project=settings.gcp.project_id,
            credentials=gcp_auth.credentials if gcp_auth.has_service_account() else None,
            model_name=settings.gcp.vertex.embedding.model,
            location=settings.gcp.vertex.embedding.location
        )

        logger.info("Initializing PGVector")
        self._db = PGVector(
            connection=settings.db.vector_db.connection_string,
            collection_name=settings.db.vector_db.collection_name,
            embeddings=self._embedding,
            use_jsonb=True
        )

    @property
    def embedding(self) -> VertexAIEmbeddings:
        """
        Returns the Vertex AI embeddings instance.

        :return: VertexAIEmbeddings instance.
        """
        return self._embedding

    @property
    def db(self) -> PGVector:
        """
        Returns the PGVector database instance.

        :return: PGVector instance.
        """
        return self._db
