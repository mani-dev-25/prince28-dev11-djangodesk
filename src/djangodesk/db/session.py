"""Async SQLAlchemy engine and database session factory."""

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from djangodesk.config import get_settings


def make_engine(settings):
    """Create an async database engine."""
    return create_async_engine(
        settings.database_url,
        echo=settings.log_level == "DEBUG",
        pool_pre_ping=True,
    )


def make_sessionmaker(engine):
    """Create a reusable async session factory."""
    return async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


settings = get_settings()
engine = make_engine(settings)
SessionFactory = make_sessionmaker(engine)


async def get_session():
    """Provide an async database session."""
    async with SessionFactory() as session:
        yield session
