"""Liveness (/health) and readiness (/ready)."""

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from djangodesk.api.deps import StoreDep

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict:
    """Alive check: touches nothing else."""
    return {"status": "ok"}


@router.get("/ready")
def ready(store: StoreDep) -> JSONResponse:
    """Ready check: are the records loaded?"""
    ok = store.loaded
    body = {"status": "ready" if ok else "not ready", "checks": {"records_loaded": ok}}
    return JSONResponse(body, status_code=200 if ok else 503)
