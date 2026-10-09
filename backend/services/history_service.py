"""
services/history_service.py — Project History Business Logic
=============================================================
Retrieves the authenticated user's design project history from the database.

Functions
---------
get_user_history()        Return a paginated list of the user's projects.
get_project_detail()      Return full details for a single project.
delete_project()          Soft-delete or hard-delete a project record.
"""

from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from database.models import Project, UploadedImage, User
from schemas.response_schema import HistoryItemResponse, HistoryResponse
from utils.helpers import format_datetime
from utils.logger import get_logger

logger = get_logger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _project_to_history_item(project: Project) -> HistoryItemResponse:
    """
    Convert a Project ORM object to a HistoryItemResponse schema.
    """
    original_image = None
    if project.source_image:
        original_image = f"upload/images/{project.source_image.id}"
    elif project.image_id:
        original_image = f"upload/images/{project.image_id}"

    return HistoryItemResponse(
        project_id=project.id,
        image_id=project.image_id,
        title=project.title or "Untitled Project",
        status=project.status,
        original_image=original_image,
        edited_image=project.edited_image_path,
        model_3d=project.model_3d_path,
        thumbnail=project.thumbnail_path,
        prompt=project.prompt,
        target_object=project.target_object,
        created_at=format_datetime(project.created_at),
        updated_at=format_datetime(project.updated_at),
    )


# ─────────────────────────────────────────────────────────────────────────────
# Get History
# ─────────────────────────────────────────────────────────────────────────────

def get_user_history(
    db: Session,
    current_user: User,
    page: int = 1,
    page_size: int = 20,
) -> HistoryResponse:
    """
    Retrieve a paginated list of all design projects for the current user.

    Projects are returned in reverse chronological order (newest first).

    Parameters
    ----------
    db : Session
        Active SQLAlchemy database session.
    current_user : User
        The authenticated user whose history to retrieve.
    page : int
        1-based page number (default: 1).
    page_size : int
        Number of items per page (default: 20, max: 100).

    Returns
    -------
    HistoryResponse
        Contains the list of projects and the total count.
    """
    page = max(1, page)
    page_size = max(1, min(page_size, 100))
    offset = (page - 1) * page_size

    # Total count (for pagination metadata on the frontend)
    total = (
        db.query(Project)
        .filter(Project.user_id == current_user.id)
        .count()
    )

    # Paginated results, newest first
    projects: List[Project] = (
        db.query(Project)
        .filter(Project.user_id == current_user.id)
        .order_by(Project.created_at.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )

    logger.info(
        "History fetched for user=%s: %d/%d projects (page %d)",
        current_user.username,
        len(projects),
        total,
        page,
    )

    history_items = [_project_to_history_item(p) for p in projects]

    return HistoryResponse(
        projects=history_items,
        total=total,
        status="success",
    )


# ─────────────────────────────────────────────────────────────────────────────
# Get Single Project
# ─────────────────────────────────────────────────────────────────────────────

def get_project_detail(
    db: Session,
    project_id: str,
    current_user: User,
) -> HistoryItemResponse:
    """
    Retrieve the full details of a single design project.

    Parameters
    ----------
    db : Session
        Active SQLAlchemy database session.
    project_id : str
        UUID of the project to retrieve.
    current_user : User
        The authenticated user making the request.

    Returns
    -------
    HistoryItemResponse
        Detailed project information.

    Raises
    ------
    HTTPException (404)
        If the project is not found or doesn't belong to the user.
    """
    project: Optional[Project] = (
        db.query(Project)
        .filter(
            Project.id == project_id,
            Project.user_id == current_user.id,
        )
        .first()
    )

    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project '{project_id}' not found.",
        )

    logger.info("Project detail fetched: id=%s user=%s", project_id, current_user.username)
    return _project_to_history_item(project)


# ─────────────────────────────────────────────────────────────────────────────
# Delete Project
# ─────────────────────────────────────────────────────────────────────────────

def delete_project(
    db: Session,
    project_id: str,
    current_user: User,
) -> dict:
    """
    Permanently delete a project and its database record.

    Note: Associated files in storage are NOT deleted here (would be a
    separate cleanup job in production). This function only removes the DB row.

    Parameters
    ----------
    db : Session
        Active SQLAlchemy database session.
    project_id : str
        UUID of the project to delete.
    current_user : User
        The authenticated user making the request.

    Returns
    -------
    dict
        A confirmation message.

    Raises
    ------
    HTTPException (404)
        If the project is not found.
    """
    project: Optional[Project] = (
        db.query(Project)
        .filter(
            Project.id == project_id,
            Project.user_id == current_user.id,
        )
        .first()
    )

    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project '{project_id}' not found.",
        )

    # Delete associated UploadedImage record and its BYTEA data to prevent orphans
    if project.source_image:
        db.delete(project.source_image)
    elif project.image_id:
        img = db.query(UploadedImage).filter(UploadedImage.id == project.image_id).first()
        if img:
            db.delete(img)

    db.delete(project)
    db.commit()

    logger.info(
        "Project and related records deleted: id=%s user=%s", project_id, current_user.username
    )
    return {"status": "success", "message": f"Project '{project_id}' deleted."}
