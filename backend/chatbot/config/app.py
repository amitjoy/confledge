from pydantic import BaseModel, Field
from typing import List, Optional


class CorsSettings(BaseModel):
    """
    Configuration for CORS settings.
    """
    enabled: bool = Field(
        default=False,
        description=(
            "Flag indicating if CORS headers are set or not. "
            "If set to true, the CORS headers will be set to allow all origins, methods, and headers."
        )
    )
    allow_credentials: bool = Field(
        default=False,
        description="Indicate that cookies should be supported for cross-origin requests"
    )
    allow_origins: List[str] = Field(
        default=[],
        description="A list of origins that should be permitted to make cross-origin requests."
    )
    allow_origin_regex: Optional[List[str]] = Field(
        default=None,
        description="A regex string to match against origins that should be permitted to make cross-origin requests."
    )
    allow_methods: List[str] = Field(
        default=["GET"],
        description="A list of HTTP methods that should be allowed for cross-origin requests."
    )
    allow_headers: List[str] = Field(
        default=[],
        description="A list of HTTP request headers that should be supported for cross-origin requests."
    )


class KeycloakSettings(BaseModel):
    """
    Configuration for Keycloak settings.
    """
    realm: str = Field(description="The OAuth realm")
    client_id: str = Field(description="The OAuth client ID")
    client_secret: str = Field(description="The OAuth client secret")
    server_url: str = Field(description="The OpenID Auth server URL")


class VectorDBRetrieverSettings(BaseModel):
    """
    Configuration for VectorDB retriever settings.
    """
    type: str = Field(description="Type of retriever to use")
    k: int = Field(description="The number of documents to return")


class VectorDBSettings(BaseModel):
    """
    Configuration for VectorDB settings.
    """
    connection_string: str = Field(description="The connection string of the PGVector db (only SQLAlchemy format)")
    collection_name: str = Field(description="The PGVector collection name to store the embeddings")
    retriever: VectorDBRetrieverSettings = Field(description="Retriever configuration")


class VertexEmbeddingSettings(BaseModel):
    """
    Configuration for Vertex embedding settings.
    """
    model: str = Field(description="The embedding model name")
    project_id: str = Field(description="Project ID of the embedding model")
    location: str = Field(description="The location")


class ChatMemorySettings(BaseModel):
    """
    Configuration for chat memory settings.
    """
    max_token_limit: int = Field(description="Maximum token limit")


class VertexAIModelSettings(BaseModel):
    """
    Configuration for Vertex AI model settings.
    """
    name: str = Field(description="The model name")
    debug: bool = Field(description="Flag to enable the langchain debug")
    verbose: bool = Field(description="Flag to enable langchain verbosity")
    streaming: bool = Field(description="Flag to set whether results will be streamed")
    temperature: float = Field(description="Sampling temperature for the degree of randomness in token selection")
    max_output_tokens: int = Field(description="Token limit for the maximum amount of text output from one prompt")
    top_p: float = Field(
        description=(
            "Tokens are selected from most probable to least until "
            "the sum of their probabilities equals the top-p value"
        )
    )
    top_k: int = Field(
        description=(
            "How the model selects tokens for output, the next token "
            "is selected from among the top-k most probable tokens"
        )
    )


class AppDBConfiguration(BaseModel):
    """
    Configuration for the application database.
    """
    connection_string: str = Field(description="The connection string of the SQL compliant db (only SQLAlchemy format)")
    job_table_name: str = Field(description="The database table name to store the job information")
    user_table_name: str = Field(description="The database table name to store the user login information")
    session_table_name: str = Field(description="The database table name to store the session information")
    history_table_name: str = Field(description="The database table name to store the history of every session")
    user_pass_salt: str = Field(description="The salt to be used for hashing the input passwords")
    permission_table_name: str = Field(description="The database table name to store the permissions")


class DBSettings(BaseModel):
    """
    Configuration for database settings.
    """
    vector_db: VectorDBSettings = Field(description="Vector DB configuration")
    app_db: AppDBConfiguration = Field(description="Application DB configuration")


class ServerSettings(BaseModel):
    """
    Configuration for server settings.
    """
    env_name: str = Field(description="Name of the environment (dev, prod)")
    port: int = Field(default=8001, description="Port of FastAPI server, defaults to 8001")
    auth: KeycloakSettings = Field(description="Keycloak OAuth configuration")
    cors: CorsSettings = Field(default_factory=lambda: CorsSettings(enabled=False), description="CORS configuration")


class VertexSettings(BaseModel):
    """
    Configuration for Vertex settings.
    """
    service_account_path: str = Field(description="GCP service account JSON file path")
    embedding: VertexEmbeddingSettings = Field(description="Vertex embedding configuration")
    chat_memory: ChatMemorySettings = Field(description="Chat memory configuration")
    model: VertexAIModelSettings = Field(description="Vertex AI model configuration")


class GcpSettings(BaseModel):
    """
    Configuration for Google Cloud Platform (GCP) settings.
    """
    project_id: str = Field(description="The project ID on the Google Cloud Platform (GCP)")
    logger_name: str = Field(description="The logger name to be used for Google Cloud Platform (GCP)")
    vertex: VertexSettings = Field(description="Google Cloud Platform (GCP) vertex AI settings")


class OpenLLMetrySettings(BaseModel):
    """
    Configuration for OpenLLMetry settings.
    """
    enabled: bool = Field(description="Flag to enable OpenLLMetry")
    dsn: str = Field(description="The sentry DSN")
    batch: bool = Field(description="Flag to enable batch mode")
    exporter: str = Field(description="Exporter name")


class Settings(BaseModel):
    """
    Main settings configuration for the application.
    """
    version: str = Field(description="The version of the application")
    mount_point: str = Field(description="The mount point for the persistent storage")
    log_level: str = Field(description="The global log level of the application")
    otel: OpenLLMetrySettings = Field(description="OpenLLMetry settings")
    server: ServerSettings = Field(description="Server configuration")
    db: DBSettings = Field(description="DB configuration")
    gcp: GcpSettings = Field(description="The configuration for Google Cloud Platform")
