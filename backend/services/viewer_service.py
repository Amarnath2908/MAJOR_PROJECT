"""
services/viewer_service.py — 3D Model Generation Business Logic
================================================================
Handles the 3D model generation pipeline.

At this stage, ALL AI calls are MOCKED.
When InstantMesh / depth estimation is integrated, only the
_run_3d_generation() function changes.

Functions
---------
_run_3d_generation()   Internal: calls the mesh generator AI module (mock).
generate_3d_model()    Public: validates project, calls AI, updates DB, returns response.
"""

from pathlib import Path

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from ai.mesh_generator import MeshGenerator
from config import BASE_DIR, settings
from database.models import Project, User
from schemas.prompt_schema import Generate3DRequest, Generate3DResponse
from services.upload_service import ensure_image_on_disk
from utils.helpers import generate_uuid
from utils.logger import get_logger

logger = get_logger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# AI Module Instance
# ─────────────────────────────────────────────────────────────────────────────

_mesh_gen = MeshGenerator()


# ─────────────────────────────────────────────────────────────────────────────
# Internal 3D Generation Runner
# ─────────────────────────────────────────────────────────────────────────────

def _run_3d_generation(image_path: str) -> str:
    """
    Delegate 3D model generation to the AI module.

    Parameters
    ----------
    image_path : str
        Path to the edited (or source) image to convert to 3D.

    Returns
    -------
    str
        Relative path to the generated .glb model file.
    """
    logger.debug("Running 3D generation on: %s", image_path)
    model_path = _mesh_gen.generate(image_path)
    logger.debug("3D model path: %s", model_path)
    return model_path


# ─────────────────────────────────────────────────────────────────────────────
# Main 3D Generation Entry Point
# ─────────────────────────────────────────────────────────────────────────────

def generate_3d_model(
    db: Session,
    request: Generate3DRequest,
    current_user: User,
) -> Generate3DResponse:
    """
    Run the full 3D model generation pipeline.

    Steps
    -----
    1. Retrieve the Project and verify ownership.
    2. Determine the input image: prefer the edited image, fall back to original.
    3. Call the AI mesh generator (currently mock).
    4. Persist the 3D model path in the Project record.
    5. Return a structured Generate3DResponse.

    Parameters
    ----------
    db : Session
        Active SQLAlchemy database session.
    request : Generate3DRequest
        Contains the ``project_id`` to generate a model for.
    current_user : User
        The authenticated user making the request.

    Returns
    -------
    Generate3DResponse
        Project UUID and path to the generated .glb model.

    Raises
    ------
    HTTPException (404)
        If the project is not found or doesn't belong to the user.
    HTTPException (400)
        If the project has no image to work from.
    HTTPException (500)
        If generation or DB update fails.
    """
    # ── Step 1: Look up Project ───────────────────────────────────────────────
    project: Project = (
        db.query(Project)
        .filter(
            Project.id == request.project_id,
            Project.user_id == current_user.id,
        )
        .first()
    )

    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project '{request.project_id}' not found.",
        )

    logger.info(
        "Starting 3D generation for project_id=%s user=%s",
        project.id,
        current_user.username,
    )

    # ── Step 2: Determine input image ─────────────────────────────────────────
    # Prefer the AI-edited image; fall back to the original upload if no edit exists.
    input_image_path = project.edited_image_path

    if input_image_path:
        # If edited image is missing from disk but stored in PostgreSQL BYTEA, re-hydrate it
        disk_edited = BASE_DIR / input_image_path
        if not disk_edited.exists() and project.edited_image_data:
            disk_edited.parent.mkdir(parents=True, exist_ok=True)
            disk_edited.write_bytes(project.edited_image_data)
            logger.info("Re-hydrated edited image from PostgreSQL to %s", disk_edited)
    elif project.source_image:
        disk_source = ensure_image_on_disk(project.source_image)
        input_image_path = str(disk_source)

    if not input_image_path:
        # Check request override
        if request.image_id:
            input_image_path = f"storage/uploads/{request.image_id}"
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "This project has no image to generate a 3D model from. "
                    "Please upload an image and run the editor first."
                ),
            )

    # ── Step 3: Call AI mesh generator (mock) ─────────────────────────────────
    try:
        model_path = _run_3d_generation(input_image_path)
    except Exception as exc:
        logger.error("3D generation failed for project %s: %s", project.id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="3D model generation failed. Please try again.",
        ) from exc

    # ── Step 4: Persist result in Project ─────────────────────────────────────
    project.model_3d_path = model_path
    project.status = "model_ready"

    try:
        db.commit()
        db.refresh(project)
        logger.info(
            "3D generation complete: project_id=%s model=%s",
            project.id,
            model_path,
        )
    except Exception as exc:
        db.rollback()
        logger.error("DB commit failed during 3D generation: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save 3D model result. Please try again.",
        ) from exc

    # ── Step 5: Return response ───────────────────────────────────────────────
    return Generate3DResponse(
        project_id=project.id,
        model=model_path,
        status="success",
        message="3D model generated successfully.",
    )
