"""Dependencies: database sessions and document repository."""

from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from djangodesk.db.repository import DocumentRepository


async def get_session(request: Request):
    """Provide one database session per request."""
    session_factory = request.app.state.session_factory
    async with session_factory() as session:
        yield session


async def get_repo(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> DocumentRepository:
    """Provide the document repository."""
    return DocumentRepository(session)


async def check_db(request: Request) -> bool:
    """Check whether PostgreSQL is reachable."""
    try:
        async with request.app.state.session_factory() as session:
            await session.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


RepoDep = Annotated[DocumentRepository, Depends(get_repo)]
