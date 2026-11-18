"""Liveness (/health) and readiness (/ready)."""

from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from djangodesk.api.deps import check_db

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict:
    """Alive check: touches nothing else."""
    return {"status": "ok"}


@router.get("/ready")
async def ready(
    database_ok: Annotated[bool, Depends(check_db)],
) -> JSONResponse:
    """Ready check: verifies the database connection."""
    body = {
        "status": "ready" if database_ok else "not ready",
        "checks": {"database": database_ok},
    }
    return JSONResponse(body, status_code=200 if database_ok else 503)
