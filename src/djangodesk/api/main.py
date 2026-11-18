"""The app factory: builds and wires the FastAPI app."""

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from djangodesk.api.errors import register_error_handlers
from djangodesk.api.middleware import RequestContextMiddleware
from djangodesk.api.routes import documents, health
from djangodesk.config import Settings, get_settings
from djangodesk.db.session import make_engine, make_sessionmaker
from djangodesk.logging_setup import setup_logging

logger = logging.getLogger(__name__)


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        setup_logging(settings.log_level)

        engine = make_engine(settings)
        app.state.engine = engine
        app.state.session_factory = make_sessionmaker(engine)

        logger.info("app started", extra={"fields": {"env": settings.app_env}})
        yield

        await engine.dispose()
        logger.info("app stopping")

    app = FastAPI(title=settings.app_name, lifespan=lifespan)
    app.add_middleware(RequestContextMiddleware)
    register_error_handlers(app)
    app.include_router(health.router)
    app.include_router(documents.router)

    return app
