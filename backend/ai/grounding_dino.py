"""
ai/grounding_dino.py — Real GroundingDINO Object Detection Service
==================================================================
Replaces the previous mock implementation.

Key design decisions:
- Model is loaded ONCE at module import time via a singleton.
- All paths come from environment variables (never hardcoded).
- The GroundingDINO installation remains at D:/AI/GroundingDINO.
- Returns structured detection dicts with pixel bounding boxes.
- CPU-safe: works without CUDA.
"""

import os
import sys
import time
import uuid
from pathlib import Path
from typing import List, Dict, Any

from config import settings
from utils.logger import get_logger

logger = get_logger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Environment Configuration
# ─────────────────────────────────────────────────────────────────────────────

GROUNDING_DINO_ROOT      = getattr(settings, "GROUNDING_DINO_ROOT", None)
DINO_CONFIG_PATH         = getattr(settings, "GROUNDING_DINO_CONFIG_PATH", None)
DINO_CHECKPOINT_PATH     = getattr(settings, "GROUNDING_DINO_CHECKPOINT_PATH", None)
DEVICE                   = getattr(settings, "DEVICE", "cpu")
BOX_THRESHOLD            = float(getattr(settings, "GROUNDING_DINO_BOX_THRESHOLD", 0.30))
TEXT_THRESHOLD           = float(getattr(settings, "GROUNDING_DINO_TEXT_THRESHOLD", 0.25))


# ─────────────────────────────────────────────────────────────────────────────
# Path Validation
# ─────────────────────────────────────────────────────────────────────────────

def _validate_dino_paths() -> None:
    """Verify that the DINO config and checkpoint files exist on disk."""
    missing = []
    if not DINO_CONFIG_PATH:
        missing.append("GROUNDING_DINO_CONFIG_PATH is not set in .env")
    elif not Path(DINO_CONFIG_PATH).exists():
        missing.append(f"DINO config not found: {DINO_CONFIG_PATH}")
    if not DINO_CHECKPOINT_PATH:
        missing.append("GROUNDING_DINO_CHECKPOINT_PATH is not set in .env")
    elif not Path(DINO_CHECKPOINT_PATH).exists():
        missing.append(f"DINO checkpoint not found: {DINO_CHECKPOINT_PATH}")
    if missing:
        for m in missing:
            logger.error("Missing file: %s", m)
        raise RuntimeError(
            "GroundingDINO model files not configured or not found. "
            "Set GROUNDING_DINO_CONFIG_PATH and GROUNDING_DINO_CHECKPOINT_PATH in backend/.env. "
            f"Details: {'; '.join(missing)}"
        )



# ─────────────────────────────────────────────────────────────────────────────
# Singleton Model Loader
# ─────────────────────────────────────────────────────────────────────────────

_dino_model = None


def _get_dino_model():
    """
    Load GroundingDINO model once and cache it for subsequent calls.
    Thread-safe for single-process FastAPI (default uvicorn mode).
    """
    global _dino_model
    if _dino_model is not None:
        return _dino_model

    logger.info("Initialising GroundingDINO model...")
    logger.info("  Config:     %s", DINO_CONFIG_PATH)
    logger.info("  Checkpoint: %s", DINO_CHECKPOINT_PATH)
    logger.info("  Device:     %s", DEVICE)

    _validate_dino_paths()

    try:
        from groundingdino.util.inference import load_model
        import torch

        t0 = time.time()
        model = load_model(str(DINO_CONFIG_PATH), str(DINO_CHECKPOINT_PATH), device=DEVICE)
        model.eval()
        elapsed = time.time() - t0

        logger.info("GroundingDINO loaded in %.2fs on device=%s", elapsed, DEVICE)
        _dino_model = model
        return _dino_model

    except ImportError as exc:
        logger.error("Failed to import groundingdino: %s", exc)
        raise RuntimeError(
            "GroundingDINO is not installed in this environment. "
            "Run: pip install --no-build-isolation -e D:\\AI\\GroundingDINO"
        ) from exc
    except Exception as exc:
        logger.error("Failed to load GroundingDINO model: %s", exc)
        raise RuntimeError(f"GroundingDINO model load failed: {exc}") from exc


# ─────────────────────────────────────────────────────────────────────────────
# Box Conversion
# ─────────────────────────────────────────────────────────────────────────────

def _norm_to_pixel(cx: float, cy: float, w: float, h: float,
                   img_w: int, img_h: int) -> Dict[str, int]:
    """
    Convert GroundingDINO's normalized [cx, cy, w, h] → pixel [x1, y1, x2, y2].

    Parameters
    ----------
    cx, cy : float   Normalized centre coordinates in [0, 1].
    w, h   : float   Normalized width and height in [0, 1].
    img_w  : int     Image width in pixels.
    img_h  : int     Image height in pixels.

    Returns
    -------
    dict with keys x1, y1, x2, y2 clamped to image boundaries.
    """
    x1 = max(0, int((cx - w / 2) * img_w))
    y1 = max(0, int((cy - h / 2) * img_h))
    x2 = min(img_w, int((cx + w / 2) * img_w))
    y2 = min(img_h, int((cy + h / 2) * img_h))
    return {"x1": x1, "y1": y1, "x2": x2, "y2": y2}


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────

def detect_objects(
    image_path: str | Path,
    prompt: str,
    box_threshold: float | None = None,
    text_threshold: float | None = None,
) -> List[Dict[str, Any]]:
    """
    Detect objects in an image using GroundingDINO open-vocabulary detection.

    Parameters
    ----------
    image_path : str or Path
        Absolute path to the image file on disk.
    prompt : str
        Natural-language text describing the objects to detect,
        e.g. ``"sofa"`` or ``"sofa . chair . table"``.
    box_threshold : float, optional
        Minimum confidence for a bounding box. Defaults to env var.
    text_threshold : float, optional
        Minimum confidence for text matching. Defaults to env var.

    Returns
    -------
    List[dict]
        Each dict contains:
        - object_id   : unique UUID string
        - label       : detected object class (str)
        - confidence  : float in [0, 1]
        - bbox        : dict with x1, y1, x2, y2 in pixels
        - norm_box    : [cx, cy, w, h] normalized (for internal use)
    """
    image_path = Path(image_path)
    if not image_path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    box_thr  = box_threshold  if box_threshold  is not None else BOX_THRESHOLD
    text_thr = text_threshold if text_threshold is not None else TEXT_THRESHOLD

    logger.info(
        "DINO detect | image=%s prompt='%s' box_thr=%.2f text_thr=%.2f",
        image_path.name, prompt, box_thr, text_thr,
    )

    model = _get_dino_model()

    try:
        import torch
        from PIL import Image
        from groundingdino.util.inference import load_image, predict

        # load_image returns (numpy_rgb_array, transformed_tensor)
        image_source, image_tensor = load_image(str(image_path))
        img_h, img_w = image_source.shape[:2]

        logger.info("Image size: %dx%d", img_w, img_h)

        t0 = time.time()
        with torch.no_grad():
            boxes, logits, phrases = predict(
                model=model,
                image=image_tensor,
                caption=prompt,
                box_threshold=box_thr,
                text_threshold=text_thr,
                device=DEVICE,
            )
        elapsed = time.time() - t0

        logger.info(
            "DINO inference complete: %d detection(s) in %.2fs",
            len(boxes), elapsed,
        )

        detections: List[Dict[str, Any]] = []
        for box, logit, phrase in zip(boxes.tolist(), logits.tolist(), phrases):
            cx, cy, w, h = box
            bbox = _norm_to_pixel(cx, cy, w, h, img_w, img_h)
            obj_id = str(uuid.uuid4())
            det = {
                "object_id": obj_id,
                "label": phrase.strip(),
                "confidence": round(float(logit), 4),
                "bbox": bbox,
                "norm_box": [round(v, 6) for v in box],
                "image_width": img_w,
                "image_height": img_h,
            }
            logger.info(
                "  [%s] label='%s' conf=%.4f bbox=%s",
                obj_id[:8], det["label"], det["confidence"], bbox,
            )
            detections.append(det)

        return detections

    except Exception as exc:
        logger.error("GroundingDINO inference failed: %s", exc, exc_info=True)
        raise RuntimeError(f"GroundingDINO detection failed: {exc}") from exc


# ─────────────────────────────────────────────────────────────────────────────
# Legacy Mock-Compatible Class (preserves import compatibility)
# ─────────────────────────────────────────────────────────────────────────────

class GroundingDINO:
    """
    Backwards-compatible wrapper so existing analysis_service.py imports
    continue to work while we transition to the new detect_objects() function.
    """

    def __init__(self) -> None:
        logger.info("GroundingDINO wrapper initialised (real model via singleton).")

    def detect(self, image: str, text_prompt: str = "sofa") -> List[str]:
        """
        Legacy-compatible detect() for analysis_service.
        Returns list of label strings (for backwards compat with old schema).
        """
        try:
            detections = detect_objects(image, text_prompt)
            labels = [d["label"] for d in detections]
            logger.info("GroundingDINO.detect() -> labels: %s", labels)
            return labels if labels else ["No objects detected"]
        except Exception as exc:
            logger.error("GroundingDINO.detect() failed: %s", exc)
            return []
