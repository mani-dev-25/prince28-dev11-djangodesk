"""Every error leaves the API as RFC 9457 problem details."""

from http import HTTPStatus

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from djangodesk.logging_setup import request_id_var

PROBLEM_JSON = "application/problem+json"


def problem_response(
    status: int, detail: str, instance: str, errors: list[dict] | None = None
) -> JSONResponse:
    """Build one problem-details response."""
    try:
        title = HTTPStatus(status).phrase
    except ValueError:
        title = "Error"
    body = {
        "type": "about:blank",
        "title": title,
        "status": status,
        "detail": detail,
        "instance": instance,
        "request_id": request_id_var.get(),
    }
    if errors:
        body["errors"] = errors
    return JSONResponse(body, status_code=status, media_type=PROBLEM_JSON)


async def http_error_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    return problem_response(exc.status_code, str(exc.detail), request.url.path)


async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    errors = [
        {"field": ".".join(str(part) for part in err["loc"]), "message": err["msg"]}
        for err in exc.errors()
    ]
    return problem_response(422, "Request validation failed.", request.url.path, errors)


def register_error_handlers(app: FastAPI) -> None:
    """Tell FastAPI to use our handlers instead of its defaults."""
    app.add_exception_handler(StarletteHTTPException, http_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
