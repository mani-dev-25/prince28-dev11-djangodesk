"""GET /v1/documents and GET /v1/documents/{record_id}."""

from typing import Annotated

from fastapi import APIRouter, HTTPException, Query

from djangodesk.api.deps import StoreDep

router = APIRouter(prefix="/v1/documents", tags=["documents"])


@router.get("")
def list_documents(
    store: StoreDep,
    q: Annotated[str | None, Query(description="Search text")] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> dict:
    """List records, optionally filtered by text, one page at a time."""
    records = store.search(q) if q else store.records
    return {
        "total": len(records),
        "limit": limit,
        "offset": offset,
        "items": records[offset : offset + limit],
    }


@router.get("/{record_id}")
def get_document(record_id: str, store: StoreDep) -> dict:
    """Return one record or a 404."""
    record = store.get(record_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"No document with id '{record_id}'.")
    return record
