"""GET /v1/documents and GET /v1/documents/{record_id}."""

from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, Request

from djangodesk.api.deps import RepoDep
from djangodesk.db.repository import FILTER_KEY

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("")
async def list_documents(
    request: Request,
    repo: RepoDep,
    q: Annotated[str | None, Query(description="Search text")] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> dict:
    """List documents with text search and metadata filters."""

    reserved = {"q", "limit", "offset"}
    filters: dict[str, str] = {}

    for key, value in request.query_params.multi_items():
        if key in reserved:
            continue

        if not FILTER_KEY.fullmatch(key):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid filter key: '{key}'",
            )

        filters[key] = value

    total, items = await repo.list(
        q=q,
        filters=filters,
        limit=limit,
        offset=offset,
    )

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "filters": filters,
        "items": items,
    }


@router.get("/{record_id}")
async def get_document(record_id: str, repo: RepoDep) -> dict:
    """Return one document or a 404."""
    document = await repo.get(record_id)

    if document is None:
        raise HTTPException(
            status_code=404,
            detail=f"No document with id '{record_id}'.",
        )

    return document
