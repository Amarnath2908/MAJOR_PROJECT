"""
api/editor.py — Image Editor API Routes
=========================================
Defines HTTP endpoints for AI-powered image editing.
Currently returns mock edited image paths.

Endpoints
---------
POST /editor/edit   → Edit an image using a natural language prompt.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from database.database import get_db
from database.models import User
from middleware.auth import get_current_user
from schemas.prompt_schema import (
    ApproveProjectRequest,
    ApproveProjectResponse,
    EditRequest,
    EditResponse,
)
from services import editor_service
from utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


# ─────────────────────────────────────────────────────────────────────────────
# Edit Image
# ─────────────────────────────────────────────────────────────────────────────

@router.post(
    "/edit",
    response_model=EditResponse,
    status_code=status.HTTP_200_OK,
    summary="Edit an image with a natural language prompt",
    description=(
        "Apply a text-guided edit to a previously uploaded image. "
        "Example prompts: 'Change the sofa to dark navy', 'Add a window'. "
        "**Currently returns mock data.** "
        "Real SAM + Stable Diffusion inpainting will be integrated here."
    ),
)
def edit_image(
    request: EditRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> EditResponse:
    logger.info(
        "Edit request: image_id=%s user=%s prompt='%s'",
        request.image_id,
        current_user.username,
        request.prompt,
    )
    return editor_service.edit_image(db, request, current_user)


# ─────────────────────────────────────────────────────────────────────────────
# Approve Design
# ─────────────────────────────────────────────────────────────────────────────

@router.post(
    "/approve",
    response_model=ApproveProjectResponse,
    status_code=status.HTTP_200_OK,
    summary="Approve customized design project",
    description="Mark a design project as approved and ready for 3D model generation.",
)
def approve_design(
    request: ApproveProjectRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApproveProjectResponse:
    logger.info(
        "Approval request: project_id=%s user=%s",
        request.project_id,
        current_user.username,
    )
    return editor_service.approve_project(db, request.project_id, current_user)
