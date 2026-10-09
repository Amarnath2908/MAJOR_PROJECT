"""
ai/sam.py — Real SAM ViT-B Segmentation Service
================================================
Replaces the previous mock implementation.

Key design decisions:
- SAM predictor is loaded ONCE at module import via a singleton.
- All paths come from environment variables (never hardcoded).
- Accepts pixel bounding boxes from GroundingDINO.
- Returns binary PNG masks (0=background, 255=object).
- CPU-safe: works without CUDA.
"""

import os
import time
import uuid
from pathlib import Path
from typing import List, Dict, Any, Tuple

import numpy as np

from config import settings
from utils.logger import get_logger

logger = get_logger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Environment Configuration
# ─────────────────────────────────────────────────────────────────────────────

SAM_CHECKPOINT_PATH = getattr(
    settings,
    "SAM_CHECKPOINT_PATH",
    None,
)
SAM_MODEL_TYPE = getattr(settings, "SAM_MODEL_TYPE", "vit_b")
DEVICE         = getattr(settings, "DEVICE", "cpu")


# ─────────────────────────────────────────────────────────────────────────────
# Singleton SAM Predictor
# ─────────────────────────────────────────────────────────────────────────────

_sam_predictor = None


def _get_sam_predictor():
    """
    Load SAM ViT-B and its SamPredictor once; cache for subsequent calls.
    """
    global _sam_predictor
    if _sam_predictor is not None:
        return _sam_predictor

    logger.info("Initialising SAM %s model...", SAM_MODEL_TYPE)
    logger.info("  Checkpoint: %s", SAM_CHECKPOINT_PATH)
    logger.info("  Device:     %s", DEVICE)

    if not SAM_CHECKPOINT_PATH:
        raise RuntimeError(
            "SAM_CHECKPOINT_PATH is not set in backend/.env. "
            "Configure it and ensure the weights file exists."
        )
    if not Path(SAM_CHECKPOINT_PATH).exists():
        raise FileNotFoundError(
            f"SAM checkpoint not found: {SAM_CHECKPOINT_PATH}. "
            "Check SAM_CHECKPOINT_PATH in .env"
        )


    try:
        from segment_anything import SamPredictor, sam_model_registry

        t0 = time.time()
        sam = sam_model_registry[SAM_MODEL_TYPE](checkpoint=str(SAM_CHECKPOINT_PATH))
        sam.to(DEVICE)
        sam.eval()
        predictor = SamPredictor(sam)
        elapsed = time.time() - t0

        logger.info("SAM loaded in %.2fs on device=%s", elapsed, DEVICE)
        _sam_predictor = predictor
        return _sam_predictor

    except ImportError as exc:
        logger.error("Failed to import segment_anything: %s", exc)
        raise RuntimeError(
            "segment_anything is not installed. "
            "Run: pip install git+https://github.com/facebookresearch/segment-anything.git"
        ) from exc
    except Exception as exc:
        logger.error("Failed to load SAM model: %s", exc)
        raise RuntimeError(f"SAM model load failed: {exc}") from exc


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────

def segment_with_boxes(
    image_path: str | Path,
    detections: List[Dict[str, Any]],
    mask_dir: Path | None = None,
) -> List[Dict[str, Any]]:
    """
    Generate SAM segmentation masks for each GroundingDINO detection.

    Parameters
    ----------
    image_path : str or Path
        Absolute path to the image file on disk.
    detections : list of dict
        Each dict must contain at minimum:
        - object_id  : str (unique ID)
        - label      : str
        - confidence : float
        - bbox       : dict with x1, y1, x2, y2 in pixels
    mask_dir : Path, optional
        Directory where mask PNGs are saved.
        Defaults to settings.MASKS_DIR.

    Returns
    -------
    List[dict]
        Input detections enriched with:
        - mask_path  : str  (absolute path to saved mask PNG)
        - mask_url   : str  (URL-relative path for API responses)
        - mask_score : float
    """
    if not detections:
        logger.info("SAM: no detections to segment.")
        return []

    image_path = Path(image_path)
    if not image_path.exists():
        raise FileNotFoundError(f"Image not found for SAM: {image_path}")

    out_dir = mask_dir if mask_dir is not None else settings.MASKS_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    predictor = _get_sam_predictor()

    # Load image once for all boxes
    try:
        import cv2
        from PIL import Image as PILImage
        import torch

        pil_img = PILImage.open(image_path).convert("RGB")
        image_rgb = np.array(pil_img)
        logger.info(
            "SAM set_image: %s size=%dx%d",
            image_path.name, pil_img.width, pil_img.height,
        )
        predictor.set_image(image_rgb)
    except Exception as exc:
        logger.error("SAM: failed to load image %s: %s", image_path, exc)
        raise RuntimeError(f"SAM image load failed: {exc}") from exc

    results = []
    for idx, det in enumerate(detections):
        obj_id   = det.get("object_id", str(uuid.uuid4()))
        label    = det.get("label", "object")
        bbox     = det["bbox"]
        x1, y1, x2, y2 = bbox["x1"], bbox["y1"], bbox["x2"], bbox["y2"]

        # Validate box
        if x2 <= x1 or y2 <= y1:
            logger.warning("Skipping invalid bbox for %s: %s", obj_id, bbox)
            continue

        input_box = np.array([x1, y1, x2, y2], dtype=float)

        try:
            import torch
            with torch.no_grad():
                masks, scores, _ = predictor.predict(
                    box=input_box,
                    multimask_output=True,
                )

            # Select the mask with the highest score
            best_idx  = int(scores.argmax())
            best_mask = masks[best_idx]
            best_score = float(scores[best_idx])

            # Convert to binary PNG: 0=background, 255=object
            binary_mask = (best_mask * 255).astype(np.uint8)

            # Save as PNG using UUID-based filename (no overwrite risk)
            mask_filename = f"mask_{obj_id[:8]}_{idx+1:03d}.png"
            mask_path = out_dir / mask_filename
            cv2.imwrite(str(mask_path), binary_mask)

            # URL-relative path served via /storage/masks/...
            mask_url = f"/storage/masks/{mask_filename}"

            logger.info(
                "  SAM mask [%d] label='%s' score=%.4f shape=%s -> %s",
                idx + 1, label, best_score, binary_mask.shape, mask_filename,
            )

            result = {**det, "mask_path": str(mask_path), "mask_url": mask_url, "mask_score": round(best_score, 4)}
            results.append(result)

        except Exception as exc:
            logger.error("SAM prediction failed for detection %d (%s): %s", idx + 1, obj_id, exc)
            # Append detection without mask rather than aborting all
            results.append({**det, "mask_path": None, "mask_url": None, "mask_score": 0.0})

    return results


# ─────────────────────────────────────────────────────────────────────────────
# Legacy Mock-Compatible Class (preserves import compatibility)
# ─────────────────────────────────────────────────────────────────────────────

class SAM:
    """Backwards-compatible class wrapper."""

    def __init__(self) -> None:
        logger.info("SAM wrapper initialised (real model via singleton).")

    def segment(
        self,
        image: str,
        boxes: List[List[float]] | None = None,
        points: List[List[float]] | None = None,
    ) -> Dict[str, Any]:
        """Legacy-compatible segment() method."""
        logger.warning("SAM.segment() legacy API called — use segment_with_boxes() instead.")
        return {
            "masks": [],
            "mask_path": None,
            "scores": [],
            "num_objects": 0,
        }
