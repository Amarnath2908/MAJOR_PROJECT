"""
api/history.py — Project History API Routes
=============================================
Defines HTTP endpoints for retrieving and managing project history.

Endpoints
---------
GET  /history/              → List all projects for the current user.
GET  /history/{project_id}  → Get detailed info for a single project.
DELETE /history/{project_id} → Delete a project.
"""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from database.database import get_db
from database.models import User
from middleware.auth import get_current_user
from schemas.response_schema import HistoryItemResponse, HistoryResponse
from services import history_service
from utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


# ─────────────────────────────────────────────────────────────────────────────
# List Project History
# ─────────────────────────────────────────────────────────────────────────────

@router.get(
    "/",
    response_model=HistoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get the current user's project history",
    description=(
        "Returns a paginated list of all design projects created by the "
        "authenticated user, ordered from newest to oldest. "
        "Each project includes its status, image paths, and prompts."
    ),
)
def get_history(
    page: int = Query(default=1, ge=1, description="Page number (1-indexed)."),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page (max 100)."),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> HistoryResponse:
    """
    Return a paginated list of the user's design projects.

    Parameters
    ----------
    page : int
        Page number, 1-indexed. Default: 1.
    page_size : int
        Number of projects per page. Range: 1–100. Default: 20.
    current_user : User
        Authenticated user.
    db : Session
        Injected database session.

    Returns
    -------
    HistoryResponse
        List of HistoryItemResponse + total count.

    Example Response
    ----------------
    {
        "projects": [
            {
                "project_id": "a1b2c3d4-...",
                "title": "Living Room Redesign",
                "status": "model_ready",
                "original_image": "storage/uploads/abc.jpg",
                "edited_image": "storage/edited/def.png",
                "model_3d": "storage/models3d/ghi.glb",
                "prompt": "Paint the walls light grey",
                "created_at": "2026-07-30T09:00:00+00:00"
            }
        ],
        "total": 1,
        "status": "success"
    }
    """
    logger.info(
        "History request: user=%s page=%d page_size=%d",
        current_user.username, page, page_size,
    )
    return history_service.get_user_history(db, current_user, page, page_size)


# ─────────────────────────────────────────────────────────────────────────────
# Get Single Project
# ─────────────────────────────────────────────────────────────────────────────

@router.get(
    "/{project_id}",
    response_model=HistoryItemResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a single project's details",
    description="Retrieve full details for a specific design project by its UUID.",
)
def get_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> HistoryItemResponse:
    """
    Return detailed information about a single project.

    Parameters
    ----------
    project_id : str
        UUID of the project to retrieve.
    current_user : User
        Authenticated user — must own the project.
    db : Session
        Injected database session.

    Returns
    -------
    HistoryItemResponse
        Full project details.

    Raises
    ------
    HTTPException 404
        If the project doesn't exist or belong to the user.
    """
    return history_service.get_project_detail(db, project_id, current_user)


# ─────────────────────────────────────────────────────────────────────────────
# Delete Project
# ─────────────────────────────────────────────────────────────────────────────

@router.delete(
    "/{project_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a design project",
    description="Permanently delete a design project and its database record.",
)
def delete_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """
    Delete a project by UUID.

    Parameters
    ----------
    project_id : str
        UUID of the project to delete.
    current_user : User
        Authenticated user — must own the project.
    db : Session
        Injected database session.

    Returns
    -------
    dict
        Confirmation message.

    Raises
    ------
    HTTPException 404
        If the project is not found.
    """
    return history_service.delete_project(db, project_id, current_user)
