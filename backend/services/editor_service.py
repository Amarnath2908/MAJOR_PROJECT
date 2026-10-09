"""
services/editor_service.py — Image Editing Business Logic
==========================================================
Handles the image editing pipeline.

At this stage, ALL AI calls are MOCKED.
When SAM + Stable Diffusion / FLUX are integrated, only the
_run_edit() function changes — nothing else changes.

Functions
---------
_run_edit()        Internal: delegates to the AI image editor (mock).
edit_image()       Public: validates request, calls AI, updates Project in DB.
"""

from pathlib import Path

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from ai.image_editor import ImageEditor
from config import BASE_DIR, settings
from database.models import Project, UploadedImage, User
from schemas.prompt_schema import ApproveProjectResponse, EditRequest, EditResponse
from services.upload_service import ensure_image_on_disk, get_image_by_id
from utils.helpers import format_datetime, generate_uuid
from utils.logger import get_logger

logger = get_logger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# AI Module Instance
# ─────────────────────────────────────────────────────────────────────────────

_editor = ImageEditor()


# ─────────────────────────────────────────────────────────────────────────────
# Internal Edit Runner
# ─────────────────────────────────────────────────────────────────────────────

def _run_edit(image_path: str, prompt: str) -> str:
    """
    Delegate image editing to the AI module.

    Parameters
    ----------
    image_path : str
        Path to the source image.
    prompt : str
        Natural language editing instruction.

    Returns
    -------
    str
        Relative path to the edited image (e.g. ``"storage/edited/sample.png"``).
    """
    logger.debug("Running edit on '%s' with prompt: '%s'", image_path, prompt)
    result_path = _editor.edit(image_path, prompt)
    logger.debug("Edit result path: %s", result_path)
    return result_path


# ─────────────────────────────────────────────────────────────────────────────
# Main Edit Entry Point
# ─────────────────────────────────────────────────────────────────────────────

def edit_image(
    db: Session,
    request: EditRequest,
    current_user: User,
) -> EditResponse:
    """
    Run the full image editing pipeline.

    Steps
    -----
    1. Validate the source image exists and belongs to the user.
    2. Retrieve or create the associated Project record.
    3. Call the AI image editor (currently mock).
    4. Persist the edited image path and prompt in the Project.
    5. Return a structured EditResponse.

    Parameters
    ----------
    db : Session
        Active SQLAlchemy database session.
    request : EditRequest
        Contains ``image_id`` and ``prompt``.
    current_user : User
        The authenticated user making the request.

    Returns
    -------
    EditResponse
        Project UUID, source image UUID, prompt, and edited image path.

    Raises
    ------
    HTTPException (404)
        If the image is not found.
    HTTPException (500)
        If editing or DB update fails.
    """
    # ── Step 1: Validate source image ─────────────────────────────────────────
    image: UploadedImage = get_image_by_id(
        db, request.image_id, user_id=current_user.id
    )

    logger.info(
        "Starting edit for image_id=%s user=%s prompt='%s'",
        image.id,
        current_user.username,
        request.prompt,
    )

    # ── Step 2: Retrieve or create Project ────────────────────────────────────
    project: Project | None = None

    # If the client provided an explicit project_id, look it up.
    if request.project_id:
        project = (
            db.query(Project)
            .filter(Project.id == request.project_id, Project.user_id == current_user.id)
            .first()
        )
        if project is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project '{request.project_id}' not found.",
            )
    else:
        # Otherwise find the project by image_id, or create a fresh one.
        project = db.query(Project).filter(Project.image_id == image.id).first()

    if project is None:
        project = Project(
            id=generate_uuid(),
            user_id=current_user.id,
            image_id=image.id,
            title=f"Project — {image.original_filename}",
            status="created",
        )
        db.add(project)
        logger.info("Created new Project for edit: image_id=%s", image.id)

    # ── Step 3: Call AI editor (mock) ─────────────────────────────────────────
    try:
        # Re-hydrate image from PostgreSQL BYTEA if missing on disk
        disk_path = ensure_image_on_disk(image)
        edited_image_path = _run_edit(str(disk_path), request.prompt)
    except Exception as exc:
        logger.error("Image edit failed for image %s: %s", image.id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Image editing failed. Please try again.",
        ) from exc

    # ── Step 4: Update Project record ─────────────────────────────────────────
    project.prompt = request.prompt
    if request.target_object:
        project.target_object = request.target_object
    project.edited_image_path = edited_image_path
    project.status = "edited"

    # Also persist edited image bytes in PostgreSQL BYTEA if file exists
    try:
        disk_edited = BASE_DIR / edited_image_path
        if disk_edited.exists():
            project.edited_image_data = disk_edited.read_bytes()
    except Exception as read_exc:
        logger.warning("Could not read edited image bytes for DB storage: %s", read_exc)

    # Also update the source image status and project linkage
    image.status = "edited"
    image.project_id = project.id

    try:
        db.commit()
        db.refresh(project)
        logger.info(
            "Edit complete: project_id=%s edited_image=%s target_object=%s",
            project.id,
            edited_image_path,
            project.target_object,
        )
    except Exception as exc:
        db.rollback()
        logger.error("DB commit failed during edit: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save edit results. Please try again.",
        ) from exc

    # ── Step 5: Return response ───────────────────────────────────────────────
    return EditResponse(
        project_id=project.id,
        image_id=image.id,
        prompt=request.prompt,
        target_object=project.target_object,
        edited_image=edited_image_path,
        status="success",
        message="Image edited successfully.",
    )


# ─────────────────────────────────────────────────────────────────────────────
# Approve Project
# ─────────────────────────────────────────────────────────────────────────────

def approve_project(
    db: Session,
    project_id: str,
    current_user: User,
) -> ApproveProjectResponse:
    """
    Mark a project design as approved and ready for 3D model generation.
    """
    project: Project | None = (
        db.query(Project)
        .filter(Project.id == project_id, Project.user_id == current_user.id)
        .first()
    )

    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project '{project_id}' not found.",
        )

    project.status = "approved"

    try:
        db.commit()
        db.refresh(project)
        logger.info("Project approved: id=%s user=%s", project.id, current_user.username)
    except Exception as exc:
        db.rollback()
        logger.error("DB commit failed during approve: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update project approval status.",
        ) from exc

    return ApproveProjectResponse(
        project_id=project.id,
        status="approved",
        message="Design approved successfully. Ready for 3D generation.",
    )
