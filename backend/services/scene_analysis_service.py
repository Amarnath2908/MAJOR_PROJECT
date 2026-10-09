"""
services/scene_analysis_service.py — GroundingDINO + SAM Orchestration
=======================================================================
Coordinates the full pipeline:
  uploaded image → GroundingDINO → bounding boxes → SAM → mask PNGs → results

This layer keeps model-specific logic inside ai/grounding_dino.py and
ai/sam.py. Routes and other services call this module only.
"""

import time
from pathlib import Path
from typing import List, Dict, Any

from fastapi import HTTPException, status

from ai.grounding_dino import detect_objects
from ai.sam import segment_with_boxes
from config import settings
from utils.logger import get_logger

logger = get_logger(__name__)


def run_grounded_sam(
    image_path: str | Path,
    prompt: str,
    box_threshold: float | None = None,
    text_threshold: float | None = None,
) -> List[Dict[str, Any]]:
    """
    Run the full GroundingDINO → SAM pipeline on a single image.

    Parameters
    ----------
    image_path : str or Path
        Absolute path to the image on disk.
    prompt : str
        Natural-language prompt, e.g. "sofa".
    box_threshold : float, optional
        Overrides GROUNDING_DINO_BOX_THRESHOLD env var.
    text_threshold : float, optional
        Overrides GROUNDING_DINO_TEXT_THRESHOLD env var.

    Returns
    -------
    List[dict]
        Each dict contains:
        {
            "object_id":  str,
            "label":      str,
            "confidence": float,
            "bbox":       {"x1": int, "y1": int, "x2": int, "y2": int},
            "mask_url":   str,    # /storage/masks/<filename>
            "mask_score": float,
        }

    Raises
    ------
    HTTPException 500
        If DINO or SAM fail; logs detailed error internally.
    """
    image_path = Path(image_path)
    t_start = time.time()
    logger.info(
        "run_grounded_sam | image=%s prompt='%s'",
        image_path.name, prompt,
    )

    # ── Step 1: GroundingDINO detection ───────────────────────────────────────
    try:
        detections = detect_objects(
            image_path=image_path,
            prompt=prompt,
            box_threshold=box_threshold,
            text_threshold=text_threshold,
        )
    except FileNotFoundError as exc:
        logger.error("Image not found for DINO: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image file not found on server.",
        ) from exc
    except RuntimeError as exc:
        logger.error("GroundingDINO failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Object detection failed. Please try again.",
        ) from exc

    if not detections:
        logger.info("No objects detected for prompt='%s'", prompt)
        return []

    logger.info("DINO found %d detection(s)", len(detections))

    # ── Step 2: SAM segmentation ───────────────────────────────────────────────
    try:
        results = segment_with_boxes(
            image_path=image_path,
            detections=detections,
            mask_dir=settings.MASKS_DIR,
        )
    except FileNotFoundError as exc:
        logger.error("Image not found for SAM: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image file not found for segmentation.",
        ) from exc
    except RuntimeError as exc:
        logger.error("SAM failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Segmentation failed. Please try again.",
        ) from exc

    elapsed = time.time() - t_start
    logger.info(
        "run_grounded_sam complete: %d result(s) in %.2fs",
        len(results), elapsed,
    )

    # Strip internal fields not needed in API responses
    clean_results = []
    for r in results:
        clean_results.append({
            "object_id":  r["object_id"],
            "label":      r["label"],
            "confidence": r["confidence"],
            "bbox":       r["bbox"],
            "mask_url":   r.get("mask_url"),
            "mask_score": r.get("mask_score", 0.0),
        })

    return clean_results
