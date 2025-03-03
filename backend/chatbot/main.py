import logging
import os
import sentry_sdk
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_cloud_logging import RequestLoggingMiddleware
from kink import di
from opentelemetry.sdk.trace.export import ConsoleSpanExporter
from sentry_sdk.integrations.opentelemetry import SentrySpanProcessor, SentryPropagator
from traceloop.sdk import Traceloop, Instruments

from config.app import Settings
from config.loader import ConfigLoader
from config.logger import TellyLogging

logger = logging.getLogger(__name__)


def load_settings() -> Settings:
    """
    Load application settings from the environment and configuration files.

    :return: An instance of Settings loaded with the application configuration.
    :raises ValueError: If the 'TELLY_PROFILE' environment variable is not set.
    """
    profile = os.environ.get('TELLY_PROFILE')
    if not profile or not profile.strip():
        raise ValueError("Environment variable 'TELLY_PROFILE' needs to be set")

    config_loader = ConfigLoader(profile.strip())
    settings = Settings(**config_loader.load())
    di[Settings] = settings
    return settings


def initialize_logging(settings: Settings):
    """
    Initialize the application logging.

    :param settings: The application settings.
    """
    from agent.auth.service import GCPAuth
    app_logging = TellyLogging(settings=settings, gcp_auth=di[GCPAuth])
    app_logging.init()
    di[TellyLogging] = app_logging


def load_fastapi_routes(settings: Settings) -> FastAPI:
    """
    Load and configure FastAPI routes and middleware.

    :param settings: The application settings.
    :return: An instance of FastAPI configured with routes and middleware.
    """
    from endpoint.user.router import router as user_router
    from endpoint.chat.router import router as chatbot_router
    from endpoint.session.router import router as session_router
    from endpoint.feedback.router import router as feedback_router
    from endpoint.healthcheck.router import router as healthcheck_router

    app = FastAPI(
        title="Telly",
        description="Telly Confluence Chatbot",
        summary="Telly Chatbot Application"
    )

    if settings.server.cors.enabled:
        logger.info("Adding CORS middleware")
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.server.cors.allow_origins,
            allow_credentials=settings.server.cors.allow_credentials,
            allow_methods=settings.server.cors.allow_methods,
            allow_headers=settings.server.cors.allow_headers
        )

    logger.info("Adding FastAPI Logging Middleware")
    app.add_middleware(RequestLoggingMiddleware)

    logger.info("Adding FastAPI routes")
    app.include_router(user_router)
    app.include_router(chatbot_router)
    app.include_router(session_router)
    app.include_router(feedback_router)
    app.include_router(healthcheck_router)

    return app


def configure_telemetry(settings: Settings):
    """
    Configure telemetry with Sentry and Traceloop.

    :param settings: The application settings.
    """
    if not settings.otel.enabled:
        logger.info("🚀 Telemetry is disabled")
        return

    logger.info("🚀 Configuring OpenTelemetry")

    traceloop_params = {
        "disable_batch": not settings.otel.batch,
        "app_name": "telly-backend",
        "resource_attributes": {
            "env": settings.server.env_name,
            "version": settings.version
        },
        "instruments": {Instruments.LANGCHAIN, Instruments.VERTEXAI}
    }

    exporter = settings.otel.exporter.strip()

    if exporter == "console":
        Traceloop.init(exporter=ConsoleSpanExporter(), **traceloop_params)
    elif exporter == "remote":
        sentry_sdk.init(
            dsn=settings.otel.dsn,
            enable_tracing=True,
            instrumenter="otel"
        )
        Traceloop.init(
            processor=SentrySpanProcessor(),
            propagator=SentryPropagator(),
            **traceloop_params
        )
    else:
        logger.warning(f"Unsupported exporter type: {exporter}")


def start_application():
    """
    Start the FastAPI application with configured settings.
    """
    settings = load_settings()
    initialize_logging(settings)
    configure_telemetry(settings)

    logger.info("🚀 Configuring FastAPI Routes")
    app = load_fastapi_routes(settings)

    logger.info("🚀 Starting Telly")
    uvicorn.run(
        app=app,
        host="localhost",
        port=settings.server.port,
        log_level=settings.log_level,
        forwarded_allow_ips=["127.0.0.1", "[::1]"],
        log_config=di[TellyLogging].fastapi_log_config
    )


if __name__ == '__main__':
    start_application()
