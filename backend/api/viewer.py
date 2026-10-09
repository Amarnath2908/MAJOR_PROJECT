"""
api/viewer.py — 3D Viewer API Routes
======================================
Defines HTTP endpoints for 3D model generation.
Currently returns a mock .glb model path.

Endpoints
---------
POST /viewer/generate3d   → Generate a 3D model from a project's image.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from database.database import get_db
from database.models import User
from middleware.auth import get_current_user
from schemas.prompt_schema import Generate3DRequest, Generate3DResponse
from services import viewer_service
from utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


# ─────────────────────────────────────────────────────────────────────────────
# Generate 3D Model
# ─────────────────────────────────────────────────────────────────────────────

@router.post(
    "/generate3d",
    response_model=Generate3DResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate a 3D model from an edited image",
    description=(
        "Generate a 3D mesh (.glb) from the edited image of a project. "
        "If no edited image exists, falls back to the original upload. "
        "**Currently returns mock data.** "
        "Real InstantMesh inference will be integrated here."
    ),
)
def generate_3d(
    request: Generate3DRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Generate3DResponse:
    """
    Generate a 3D model for the given project.

    Parameters
    ----------
    request : Generate3DRequest
        Contains ``project_id`` (and optional ``image_id`` override).
    current_user : User
        Authenticated user — must own the project.
    db : Session
        Injected database session.

    Returns
    -------
    Generate3DResponse
        project_id, model path (.glb), and status.

    Raises
    ------
    HTTPException 404
        If the project is not found.
    HTTPException 400
        If the project has no image to work from.
    HTTPException 401
        If no valid Bearer token is provided.
    HTTPException 500
        If the 3D generation pipeline fails.

    Example Response
    ----------------
    {
        "project_id": "a1b2c3d4-...",
        "model": "storage/models3d/sample.glb",
        "status": "success",
        "message": "3D model generated successfully."
    }
    """
    logger.info(
        "3D generation request: project_id=%s user=%s",
        request.project_id,
        current_user.username,
    )
    return viewer_service.generate_3d_model(db, request, current_user)
