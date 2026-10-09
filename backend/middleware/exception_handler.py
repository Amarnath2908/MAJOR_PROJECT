"""
middleware/exception_handler.py — Global Exception Handlers6
============================================================
Registers application-wide exception handlers on the FastAPI app.
Every error — whether raised deliberately (HTTPException) or
unexpectedly (unhandled Python exception) — is caught here and
returned as a consistent JSON envelope using ErrorResponse.

Handlers
--------
http_exception_handler        → Catches FastAPI/Starlette HTTPException (401, 404, etc.)
validation_exception_handler  → Catches Pydantic RequestValidationError (422).
generic_exception_handler     → Catches any other unhandled Python exception (500).

Usage (in main.py)
------------------
    from middleware.exception_handler import register_exception_handlers
    register_exception_handlers(app)
"""

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from utils.logger import get_logger

logger = get_logger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Handler Functions
# ─────────────────────────────────────────────────────────────────────────────

async def http_exception_handler(
    request: Request,
    exc: StarletteHTTPException,
) -> JSONResponse:
    """
    Handle all HTTP exceptions (401, 403, 404, 405, etc.).

    FastAPI raises ``HTTPException`` for deliberate errors.
    This handler formats them as the standard ErrorResponse envelope.

    Parameters
    ----------
    request : Request
        The incoming HTTP request (used for logging context).
    exc : StarletteHTTPException
        The raised exception with .status_code and .detail.

    Returns
    -------
    JSONResponse
        JSON body: {"status": "error", "message": "...", "code": <int>}

    Examples
    --------
    raise HTTPException(status_code=404, detail="Image not found.")
    →
    HTTP 404:
    {
        "status": "error",
        "message": "Image not found.",
        "detail": null,
        "code": 404
    }
    """
    logger.warning(
        "HTTP %d on %s %s — %s",
        exc.status_code,
        request.method,
        request.url.path,
        exc.detail,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "message": str(exc.detail),
            "detail": None,
            "code": exc.status_code,
        },
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """
    Handle Pydantic request validation errors (HTTP 422 Unprocessable Entity).

    Triggered when the client sends a request body that does not match
    the expected Pydantic schema (wrong types, missing required fields, etc.).

    Parameters
    ----------
    request : Request
        The incoming HTTP request.
    exc : RequestValidationError
        Contains a list of validation error details.

    Returns
    -------
    JSONResponse
        HTTP 422 with a structured list of field-level validation errors.

    Example Response
    ----------------
    {
        "status": "error",
        "message": "Request validation failed.",
        "detail": [
            {
                "field": "body.email",
                "message": "value is not a valid email address"
            }
        ],
        "code": 422
    }
    """
    errors = []
    for error in exc.errors():
        field = " → ".join(str(loc) for loc in error["loc"])
        errors.append({"field": field, "message": error["msg"]})

    logger.warning(
        "Validation error on %s %s: %s",
        request.method,
        request.url.path,
        errors,
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "status": "error",
            "message": "Request validation failed.",
            "detail": errors,
            "code": 422,
        },
    )


async def generic_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """
    Catch-all handler for any unhandled Python exception (HTTP 500).

    If an unexpected exception escapes all route and service code,
    this handler catches it, logs the full traceback, and returns a
    safe 500 response without leaking internal details.

    Parameters
    ----------
    request : Request
        The incoming HTTP request.
    exc : Exception
        Any Python exception that was not otherwise handled.

    Returns
    -------
    JSONResponse
        HTTP 500 with a generic error message.

    Example Response
    ----------------
    {
        "status": "error",
        "message": "An internal server error occurred. Please try again later.",
        "detail": null,
        "code": 500
    }
    """
    logger.error(
        "Unhandled exception on %s %s: %s",
        request.method,
        request.url.path,
        str(exc),
        exc_info=True,   # Include full stack trace in server logs
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "message": "An internal server error occurred. Please try again later.",
            "detail": None,
            "code": 500,
        },
    )
# ─────────────────────────────────────────────────────────────────────────────
# Registration Function
# ─────────────────────────────────────────────────────────────────────────────

def register_exception_handlers(app: FastAPI) -> None:
    """
    Register all global exception handlers on the FastAPI application.

    Called once from ``main.py`` during application creation so that
    all handlers are active before any request is processed.

    Parameters
    ----------
    app : FastAPI
        The FastAPI application instance to attach handlers to.
    """
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)

    logger.info("Global exception handlers registered.")









