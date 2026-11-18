"""Async SQLAlchemy engine and database session factory."""

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from djangodesk.config import get_settings

settings = get_settings()

engine = create_async_engine(
    settings.database_url,
    echo=settings.log_level == "DEBUG",
    pool_pre_ping=True,
)

SessionFactory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_session():
    """Provide an async database session."""
    async with SessionFactory() as session:
        yield session
