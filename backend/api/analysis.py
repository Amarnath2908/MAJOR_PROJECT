"""
api/analysis.py — Image Analysis API Routes
=============================================
Defines HTTP endpoints for AI-powered image analysis.

Endpoints
---------
POST /analysis/         → Legacy: scene analysis returning object name list.
POST /analysis/detect   → Real: GroundingDINO + SAM detection with masks.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from database.database import get_db
from database.models import User
from middleware.auth import get_current_user
from schemas.prompt_schema import (
    AnalysisRequest, AnalysisResponse,
    DetectRequest, DetectResponse, DetectionResult,
)
from services import analysis_service
from services.scene_analysis_service import run_grounded_sam
from services.upload_service import ensure_image_on_disk, get_image_by_id
from utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


# ─────────────────────────────────────────────────────────────────────────────
# Analyse Image
# ─────────────────────────────────────────────────────────────────────────────

@router.post(
    "/",
    response_model=AnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyse an uploaded image",
    description=(
        "Run AI object detection on a previously uploaded image. "
        "Returns a list of detected objects/scene elements (e.g. Wall, Sofa, Floor). "
        "**Currently returns mock data.** "
        "Real Grounding DINO inference will be integrated here."
    ),
)
def analyse_image(
    request: AnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AnalysisResponse:
    """
    Detect objects in an uploaded image.

    Parameters
    ----------
    request : AnalysisRequest
        Contains the ``image_id`` of the image to analyse.
    current_user : User
        Authenticated user — must own the image.
    db : Session
        Injected database session.

    Returns
    -------
    AnalysisResponse
        image_id, list of detected objects, and status.

    Raises
    ------
    HTTPException 404
        If the image is not found or doesn't belong to the user.
    HTTPException 401
        If no valid Bearer token is provided.
    HTTPException 500
        If the analysis pipeline fails.

    Example Response
    ----------------
    {
        "image_id": "f47ac10b-...",
        "objects": ["Wall", "Window", "Floor", "Sofa", "Table"],
        "status": "success",
        "message": "Image analysed successfully."
    }
    """
    logger.info(
        "Analysis request: image_id=%s user=%s",
        request.image_id,
        current_user.username,
    )
    return analysis_service.analyse_image(db, request, current_user)


# ─────────────────────────────────────────────────────────────────────────────
# GroundingDINO + SAM Detection  (real inference)
# ─────────────────────────────────────────────────────────────────────────────

@router.post(
    "/detect",
    response_model=DetectResponse,
    status_code=status.HTTP_200_OK,
    summary="Detect objects with GroundingDINO + SAM",
    description=(
        "Run real GroundingDINO object detection followed by SAM segmentation. "
        "Returns bounding boxes, confidence scores, and mask image URLs. "
        "Requires a natural-language prompt, e.g. 'sofa'."
    ),
)
def detect_objects_endpoint(
    request: DetectRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DetectResponse:
    """
    Detect and segment objects in an uploaded image.

    Parameters
    ----------
    request : DetectRequest
        Contains image_id, prompt, and optional threshold overrides.
    current_user : User
        JWT-authenticated user; must own the image.
    db : Session
        Injected database session.

    Returns
    -------
    DetectResponse
        List of detections, each with label, confidence, pixel bbox, mask_url.

    Raises
    ------
    HTTPException 401  If not authenticated.
    HTTPException 404  If image not found or not owned by user.
    HTTPException 500  If DINO or SAM inference fails.
    """
    logger.info(
        "Detect request: image_id=%s prompt='%s' user=%s",
        request.image_id, request.prompt, current_user.username,
    )

    # Validate image ownership
    image = get_image_by_id(db, request.image_id, user_id=current_user.id)

    # Ensure image is on disk (re-hydrates from PostgreSQL BYTEA if needed)
    disk_path = ensure_image_on_disk(image)

    # Run the full DINO → SAM pipeline
    raw_detections = run_grounded_sam(
        image_path=disk_path,
        prompt=request.prompt,
        box_threshold=request.box_threshold,
        text_threshold=request.text_threshold,
    )

    # Build structured response (never expose filesystem paths)
    detection_results = [
        DetectionResult(
            object_id=d["object_id"],
            label=d["label"],
            confidence=d["confidence"],
            bbox=d["bbox"],
            mask_url=d.get("mask_url"),
            mask_score=d.get("mask_score", 0.0),
        )
        for d in raw_detections
    ]

    count = len(detection_results)
    if count == 0:
        msg = f"No '{request.prompt}' objects detected in the image."
    else:
        msg = f"Detected {count} '{request.prompt}' object(s) with segmentation masks."

    logger.info("detect_objects_endpoint complete: %d result(s)", count)

    return DetectResponse(
        success=True,
        prompt=request.prompt,
        image_id=request.image_id,
        detections=detection_results,
        count=count,
        message=msg,
    )
