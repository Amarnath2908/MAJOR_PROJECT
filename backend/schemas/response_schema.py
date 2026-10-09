"""
schemas/response_schema.py — Generic API Response Envelopes
============================================================
Standard response wrappers used across the entire API.
Every endpoint wraps its payload in one of these schemas so that
the frontend always receives a consistent JSON structure.

Schemas
-------
SuccessResponse    → Generic success envelope.
ErrorResponse      → Generic error envelope.
PaginatedResponse  → Wrapper for paginated list endpoints.
HistoryItemResponse → Single item in GET /history.
HistoryResponse    → Full GET /history response.
"""

from typing import Any, List, Optional

from pydantic import BaseModel, Field


# ─────────────────────────────────────────────────────────────────────────────
# Generic Envelopes
# ─────────────────────────────────────────────────────────────────────────────

class SuccessResponse(BaseModel):
    """
    Generic success response envelope.

    All successful non-paginated API responses follow this shape.

    Attributes
    ----------
    status : str
        Always ``"success"``.
    message : str
        Human-readable description of what happened.
    data : any, optional
        The actual payload — can be any serialisable value.

    Example JSON
    ------------
    {
        "status": "success",
        "message": "Operation completed.",
        "data": { ... }
    }
    """

    status: str = "success"
    message: str = "Operation completed."
    data: Optional[Any] = None


class ErrorResponse(BaseModel):
    """
    Generic error response envelope.

    Used by the global exception handler so all errors have
    a consistent structure the frontend can rely on.

    Attributes
    ----------
    status : str
        Always ``"error"``.
    message : str
        Short description of the error.
    detail : str or None
        Optional technical details (e.g. validation errors, stack hints).
    code : int or None
        HTTP status code echoed in the body for easy client-side handling.

    Example JSON
    ------------
    {
        "status": "error",
        "message": "Image not found.",
        "detail": "No UploadedImage with id 'abc123' exists.",
        "code": 404
    }
    """

    status: str = "error"
    message: str
    detail: Optional[str] = None
    code: Optional[int] = None


# ─────────────────────────────────────────────────────────────────────────────
# Paginated List
# ─────────────────────────────────────────────────────────────────────────────

class PaginationMeta(BaseModel):
    """
    Metadata about a paginated result set.

    Attributes
    ----------
    page : int
        Current page number (1-indexed).
    page_size : int
        Number of items per page.
    total_items : int
        Total number of items across all pages.
    total_pages : int
        Total number of pages.
    """

    page: int
    page_size: int
    total_items: int
    total_pages: int


# ─────────────────────────────────────────────────────────────────────────────
# History
# ─────────────────────────────────────────────────────────────────────────────

class HistoryItemResponse(BaseModel):
    """
    Represents one project in the GET /history list.

    Attributes
    ----------
    project_id : str
        UUID of the project.
    title : str
        Project title.
    status : str
        Pipeline status (``"created"`` | ``"edited"`` | ``"model_ready"``).
    original_image : str or None
        Relative path to the source image.
    edited_image : str or None
        Relative path to the edited image (if available).
    model_3d : str or None
        Relative path to the .glb model (if available).
    thumbnail : str or None
        Relative path to the project thumbnail.
    prompt : str or None
        The last editing prompt applied.
    created_at : str or None
        ISO-8601 creation timestamp.
    updated_at : str or None
        ISO-8601 last update timestamp.

    Example JSON
    ------------
    {
        "project_id": "a1b2c3d4-...",
        "title": "Living Room Redesign",
        "status": "model_ready",
        "original_image": "storage/uploads/abc.jpg",
        "edited_image": "storage/edited/def.png",
        "model_3d": "storage/models3d/ghi.glb",
        "thumbnail": null,
        "prompt": "Paint the walls light grey",
        "created_at": "2026-07-30T09:00:00+00:00",
        "updated_at": "2026-07-30T09:05:00+00:00"
    }
    """

    project_id: str
    image_id: Optional[str] = None
    title: Optional[str] = "Untitled Project"
    status: str
    original_image: Optional[str] = None
    edited_image: Optional[str] = None
    model_3d: Optional[str] = None
    thumbnail: Optional[str] = None
    prompt: Optional[str] = None
    target_object: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    model_config = {"from_attributes": True, "protected_namespaces": ()}


class HistoryResponse(BaseModel):
    """
    Response body for GET /history.

    Attributes
    ----------
    projects : List[HistoryItemResponse]
        List of the user's design projects.
    total : int
        Total number of projects.
    status : str
        ``"success"`` on success.

    Example JSON
    ------------
    {
        "projects": [ {...}, {...} ],
        "total": 2,
        "status": "success"
    }
    """

    projects: List[HistoryItemResponse] = Field(default_factory=list)
    total: int = 0
    status: str = "success"
