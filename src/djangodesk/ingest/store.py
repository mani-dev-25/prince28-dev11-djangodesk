"""Async storage helpers for parsed document pages and parse failures.

These functions use the project's existing AsyncSession and PostgreSQL models.
They do not commit automatically: the caller controls the transaction.
"""

from collections.abc import Iterable
from typing import Any

from sqlalchemy import delete
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from djangodesk.db.models import Page, ParseFailure


def _page_values(document_id: int, parsed_page: Any) -> dict[str, Any]:
    """Convert a ParsedPage-like object into a Page row payload."""
    page_no = int(parsed_page.page_no)
    if page_no < 1:
        raise ValueError(f"page_no must be >= 1, got {page_no}")

    return {
        "document_id": document_id,
        "page_no": page_no,
        "text": str(parsed_page.text),
        "headings": list(parsed_page.headings or []),
    }


async def save_pages(
    session: AsyncSession,
    document_id: int,
    parsed_pages: Iterable[Any],
) -> int:
    """Upsert parsed pages for a document and remove stale page numbers.

    A page is uniquely identified by (document_id, page_no). This function
    updates existing rows, inserts new ones, and removes old page rows whose
    page numbers are no longer present in the latest parse.

    Returns the number of pages supplied. Does not commit.
    """
    values = [_page_values(document_id, page) for page in parsed_pages]

    if not values:
        # Avoid deleting previously stored content if a parser unexpectedly
        # returns no pages. The caller can decide whether to handle this case.
        raise ValueError("Refusing to store an empty parse result")

    page_numbers = [row["page_no"] for row in values]
    if len(page_numbers) != len(set(page_numbers)):
        raise ValueError("Parsed result contains duplicate page numbers")

    stmt = pg_insert(Page).values(values)
    stmt = stmt.on_conflict_do_update(
        constraint="uq_pages_document_page",
        set_={
            "text": stmt.excluded.text,
            "headings": stmt.excluded.headings,
        },
    )
    await session.execute(stmt)

    # Remove rows from an older parse that are not in this parse.
    await session.execute(
        delete(Page).where(
            Page.document_id == document_id,
            Page.page_no.not_in(page_numbers),
        )
    )
    return len(values)


async def record_parse_failure(
    session: AsyncSession,
    *,
    path: str,
    sha256: str,
    source_url: str | None,
    reason: str,
    detail: str = "",
) -> None:
    """Insert a parse failure or update it while incrementing attempts. Does not commit."""
    stmt = pg_insert(ParseFailure).values(
        path=path,
        sha256=sha256,
        source_url=source_url,
        reason=reason,
        detail=detail,
        attempts=1,
    )
    stmt = stmt.on_conflict_do_update(
        index_elements=[ParseFailure.path],
        set_={
            "sha256": stmt.excluded.sha256,
            "source_url": stmt.excluded.source_url,
            "reason": stmt.excluded.reason,
            "detail": stmt.excluded.detail,
            "attempts": ParseFailure.attempts + 1,
        },
    )
    await session.execute(stmt)


async def clear_parse_failure(session: AsyncSession, path: str) -> bool:
    """Remove a previous failure record after a successful parse. Does not commit."""
    result = await session.execute(delete(ParseFailure).where(ParseFailure.path == path))
    return bool(result.rowcount)


async def save_document_pages(
    session: AsyncSession,
    *,
    document_id: int,
    path: str,
    parsed_pages: Iterable[Any],
) -> int:
    """Store pages and clear the matching failure record in the same transaction."""
    count = await save_pages(session, document_id, parsed_pages)
    await clear_parse_failure(session, path)
    return count
