"""Dependencies: things routes ask FastAPI to hand them."""

from typing import Annotated

from fastapi import Depends, Request

from djangodesk.store import RecordStore


def get_store(request: Request) -> RecordStore:
    """Return the store created at startup."""
    return request.app.state.store


StoreDep = Annotated[RecordStore, Depends(get_store)]
