"""
ai/depth_estimation.py — Depth Estimation Interface
====================================================
Placeholder class for Depth Anything V2 monocular depth estimation.

When to replace this file
--------------------------
When integrating Depth Anything:
  1. pip install transformers torch
  2. Load the DepthAnythingForDepthEstimation model.
  3. Replace estimate() with real inference code.

DO NOT import transformers or download models here yet.
"""

from typing import Any, Dict
from utils.logger import get_logger

logger = get_logger(__name__)


class DepthEstimator:
    """
    Interface class for monocular depth estimation.

    In the final integration (Depth Anything V2), this class will:
    - Load the pre-trained DepthAnythingForDepthEstimation model.
    - Process an input image through the model.
    - Return a depth map array and save a visualisation to storage/depth/.

    Depth maps are used as input to the 3D mesh generator.

    At this stage, estimate() returns mock data.

    Usage
    -----
        estimator = DepthEstimator()
        result = estimator.estimate("storage/edited/sample.png")
        # → {"depth_map": [...], "depth_image_path": "storage/depth/sample.png"}
    """

    def __init__(self) -> None:
        """
        Initialise the DepthEstimator interface.

        Real implementation will:
        - Load AutoImageProcessor from HuggingFace.
        - Load DepthAnythingForDepthEstimation checkpoint.
        - Set model to eval mode on appropriate device.
        """
        logger.info(
            "DepthEstimator placeholder initialised. "
            "Real model will be loaded here during integration."
        )

    def estimate(self, image_path: str) -> Dict[str, Any]:
        """
        Estimate pixel-level depth for a given image.

        Parameters
        ----------
        image_path : str
            Relative path to the input image.

        Returns
        -------
        dict
            {
                "depth_map": list,          # 2D array of depth values
                "depth_image_path": str,    # Path to the depth visualisation PNG
                "min_depth": float,
                "max_depth": float,
            }
            Currently returns MOCK DATA.

        Real Implementation (future)
        ----------------------------
            processor = AutoImageProcessor.from_pretrained("LiheYoung/depth-anything-large-hf")
            model = AutoModelForDepthEstimation.from_pretrained(...)
            inputs = processor(images=image, return_tensors="pt")
            with torch.no_grad():
                outputs = model(**inputs)
            depth = outputs.predicted_depth
            return {"depth_map": depth.tolist(), ...}
        """
        logger.debug("[MOCK] DepthEstimator.estimate() called with '%s'", image_path)

        # ── MOCK RESPONSE ─────────────────────────────────────────────────────
        mock_result = {
            "depth_map": [],
            "depth_image_path": "storage/depth/sample_depth.png",
            "min_depth": 0.5,
            "max_depth": 10.0,
        }
        logger.info("[MOCK] Depth estimation result: %s", mock_result)
        return mock_result
