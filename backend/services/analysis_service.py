"""
services/analysis_service.py — Image Analysis Business Logic
=============================================================
Handles the analysis pipeline for uploaded images.

At this stage, ALL AI calls are MOCKED.
When Grounding DINO is integrated, only the _run_detection() function
changes — nothing else in this file or the API layer needs to change.

Functions
---------
_run_detection()    Internal: calls the AI module (currently mock).
analyse_image()     Public: validates the image, runs detection, updates DB.
"""

from typing import List

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from ai.grounding_dino import GroundingDINO
from database.models import Project, UploadedImage, User
from schemas.prompt_schema import AnalysisRequest, AnalysisResponse
from services.upload_service import ensure_image_on_disk, get_image_by_id
from utils.helpers import format_datetime, generate_uuid
from utils.logger import get_logger

import json

logger = get_logger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# AI Module Instance (placeholder at this stage)
# ─────────────────────────────────────────────────────────────────────────────

# This is the ONLY place GroundingDINO is instantiated.
# When you're ready to integrate the real model:
#   1. Update ai/grounding_dino.py with the real implementation.
#   2. Nothing else in this file or the API layer changes.
_detector = GroundingDINO()


# ─────────────────────────────────────────────────────────────────────────────
# Internal Detection Runner
# ─────────────────────────────────────────────────────────────────────────────

def _run_detection(image_path: str) -> List[str]:
    """
    Internal function that delegates to the AI detection module.

    This thin wrapper exists so that:
    - The rest of the service doesn't import from 'ai/' directly.
    - Integration tests can mock this single function.
    - Swapping the AI model only changes ai/grounding_dino.py,
      not this service.

    Parameters
    ----------
    image_path : str
        Relative or absolute path to the image file on disk.

    Returns
    -------
    List[str]
        List of detected object/scene label strings.
        Currently returns mock data from GroundingDINO.detect().
    """
    logger.debug("Running detection on: %s", image_path)
    results = _detector.detect(image_path)
    logger.debug("Detection results: %s", results)
    return results


# ─────────────────────────────────────────────────────────────────────────────
# Main Analysis Entry Point
# ─────────────────────────────────────────────────────────────────────────────

def analyse_image(
    db: Session,
    request: AnalysisRequest,
    current_user: User,
) -> AnalysisResponse:
    """
    Run the full analysis pipeline for a given image.

    Steps
    -----
    1. Look up the UploadedImage record and verify ownership.
    2. Call the AI detection module (currently mock).
    3. Store the analysis result in the associated Project (or create one).
    4. Update the UploadedImage status to 'analysed'.
    5. Return a structured AnalysisResponse.

    Parameters
    ----------
    db : Session
        Active SQLAlchemy database session.
    request : AnalysisRequest
        Contains the ``image_id`` of the image to analyse.
    current_user : User
        The authenticated user making the request.

    Returns
    -------
    AnalysisResponse
        Image UUID, detected objects list, and status.

    Raises
    ------
    HTTPException (404)
        If the image is not found or does not belong to the user.
    HTTPException (500)
        If analysis or database update fails.
    """
    # ── Step 1: Validate image exists and belongs to user ─────────────────────
    image: UploadedImage = get_image_by_id(
        db, request.image_id, user_id=current_user.id
    )

    logger.info(
        "Starting analysis for image_id=%s user=%s",
        image.id,
        current_user.username,
    )

    # ── Step 2: Run AI detection (mock) ──────────────────────────────────────
    try:
        disk_path = ensure_image_on_disk(image)
        detected_objects: List[str] = _run_detection(str(disk_path))
    except Exception as exc:
        logger.error("Detection failed for image %s: %s", image.id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Image analysis failed. Please try again.",
        ) from exc

    # ── Step 3: Upsert Project record ─────────────────────────────────────────
    # Check if a project already exists for this image
    project = db.query(Project).filter(Project.image_id == image.id).first()

    analysis_json = json.dumps({"objects": detected_objects})

    if project is None:
        project = Project(
            id=generate_uuid(),
            user_id=current_user.id,
            image_id=image.id,
            title=f"Project — {image.original_filename}",
            analysis_result=analysis_json,
            status="analysed",
        )
        db.add(project)
        logger.info("Created new Project for image_id=%s", image.id)
    else:
        project.analysis_result = analysis_json
        project.status = "analysed"
        logger.info("Updated existing Project id=%s with analysis.", project.id)

    # ── Step 4: Update image status and link project ──────────────────────────
    image.status = "analysed"
    image.project_id = project.id

    try:
        db.commit()
        db.refresh(image)
    except Exception as exc:
        db.rollback()
        logger.error("DB commit failed during analysis: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save analysis results. Please try again.",
        ) from exc

    logger.info(
        "Analysis complete for image_id=%s — detected: %s",
        image.id,
        detected_objects,
    )

    # ── Step 5: Return response ───────────────────────────────────────────────
    return AnalysisResponse(
        image_id=image.id,
        objects=detected_objects,
        status="success",
        message="Image analysed successfully.",
    )
