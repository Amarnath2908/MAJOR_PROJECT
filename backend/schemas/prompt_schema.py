"""
schemas/prompt_schema.py — AI Feature Request/Response Schemas
==============================================================
Pydantic schemas for the Analysis, Editor, and 3D Viewer endpoints.
These define what the client sends and what the server returns.

Schemas
-------
AnalysisRequest      → POST /analysis  request body.
AnalysisResponse     → POST /analysis  response.
EditRequest          → POST /editor/edit  request body.
EditResponse         → POST /editor/edit  response.
Generate3DRequest    → POST /viewer/generate3d  request body.
Generate3DResponse   → POST /viewer/generate3d  response.
"""

from typing import List, Optional

from pydantic import BaseModel, Field


# ─────────────────────────────────────────────────────────────────────────────
# Analysis
# ─────────────────────────────────────────────────────────────────────────────

class AnalysisRequest(BaseModel):
    """
    Request body for POST /analysis.

    Attributes
    ----------
    image_id : str
        UUID of a previously uploaded image to analyse.

    Example JSON
    ------------
    {
        "image_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479"
    }
    """

    image_id: str = Field(
        ...,
        description="UUID of the uploaded image to analyse.",
        examples=["f47ac10b-58cc-4372-a567-0e02b2c3d479"],
    )


class AnalysisResponse(BaseModel):
    """
    Response body for POST /analysis.

    Contains the list of objects detected in the image (mock at this stage).

    Attributes
    ----------
    image_id : str
        The UUID of the image that was analysed.
    objects : List[str]
        List of detected object/scene labels.
    status : str
        ``"success"`` on success.
    message : str
        Human-readable result message.

    Example JSON
    ------------
    {
        "image_id": "f47ac10b-...",
        "objects": ["Wall", "Window", "Floor", "Sofa", "Table"],
        "status": "success",
        "message": "Image analysed successfully."
    }
    """

    image_id: str
    objects: List[str] = Field(
        default_factory=list,
        description="List of detected objects in the image.",
    )
    status: str = "success"
    message: str = "Image analysed successfully."

    model_config = {"from_attributes": True}


# ─────────────────────────────────────────────────────────────────────────────
# GroundingDINO + SAM Detection (real inference)
# ─────────────────────────────────────────────────────────────────────────────

class BoundingBox(BaseModel):
    """Pixel bounding box returned by GroundingDINO."""
    x1: int
    y1: int
    x2: int
    y2: int


class DetectionResult(BaseModel):
    """A single object detection with its SAM mask."""

    object_id: str = Field(description="Unique UUID for this detection.")
    label: str = Field(description="Detected object label, e.g. 'sofa'.")
    confidence: float = Field(description="Detection confidence in [0, 1].")
    bbox: BoundingBox = Field(description="Pixel bounding box.")
    mask_url: Optional[str] = Field(
        default=None,
        description="URL path to the binary mask PNG, e.g. /storage/masks/...",
    )
    mask_score: float = Field(default=0.0, description="SAM mask quality score.")

    model_config = {"from_attributes": True}


class DetectRequest(BaseModel):
    """
    Request body for POST /analysis/detect.

    Attributes
    ----------
    image_id : str
        UUID of a previously uploaded image to detect objects in.
    prompt : str
        Natural-language description of objects to find, e.g. ``"sofa"``.
    box_threshold : float, optional
        Override the default GroundingDINO box confidence threshold.
    text_threshold : float, optional
        Override the default GroundingDINO text confidence threshold.

    Example JSON
    ------------
    {
        "image_id": "f47ac10b-...",
        "prompt": "sofa"
    }
    """

    image_id: str = Field(
        ...,
        description="UUID of the uploaded image to analyse.",
        examples=["f47ac10b-58cc-4372-a567-0e02b2c3d479"],
    )
    prompt: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Natural-language prompt for GroundingDINO.",
        examples=["sofa"],
    )
    box_threshold: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Optional override for box detection threshold.",
    )
    text_threshold: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Optional override for text matching threshold.",
    )


class DetectResponse(BaseModel):
    """
    Response body for POST /analysis/detect.

    Example JSON
    ------------
    {
        "success": true,
        "prompt": "sofa",
        "image_id": "f47ac10b-...",
        "detections": [
            {
                "object_id": "...",
                "label": "sofa",
                "confidence": 0.59,
                "bbox": {"x1": 712, "y1": 629, "x2": 1405, "y2": 1047},
                "mask_url": "/storage/masks/mask_abc123_001.png",
                "mask_score": 0.94
            }
        ],
        "count": 1,
        "message": "Detected 1 object(s)."
    }
    """

    success: bool = True
    prompt: str
    image_id: str
    detections: List[DetectionResult] = Field(default_factory=list)
    count: int = 0
    message: str = ""

    model_config = {"from_attributes": True}


# ─────────────────────────────────────────────────────────────────────────────
# Editor
# ─────────────────────────────────────────────────────────────────────────────

class EditRequest(BaseModel):
    """
    Request body for POST /editor/edit.

    Attributes
    ----------
    image_id : str
        UUID of the uploaded (or previously edited) image to edit.
    prompt : str
        Natural language instruction describing the desired change,
        e.g. ``"Change the wall colour to light grey and add a plant."``.
    project_id : str, optional
        If provided, the edit is attached to an existing project.

    Example JSON
    ------------
    {
        "image_id": "f47ac10b-...",
        "prompt": "Change the sofa colour to dark navy blue",
        "project_id": null
    }
    """

    image_id: str = Field(
        ...,
        description="UUID of the source image.",
        examples=["f47ac10b-58cc-4372-a567-0e02b2c3d479"],
    )
    prompt: str = Field(
        ...,
        min_length=5,
        max_length=1000,
        description="Natural language editing instruction.",
        examples=["Change the sofa colour to dark navy blue"],
    )
    project_id: Optional[str] = Field(
        default=None,
        description="Optional project UUID to attach this edit to.",
    )
    target_object: Optional[str] = Field(
        default=None,
        description="Optional detected object label identified from prompt.",
    )


class EditResponse(BaseModel):
    """
    Response body for POST /editor/edit.
    """

    project_id: str
    image_id: str
    prompt: str
    target_object: Optional[str] = None
    edited_image: str
    status: str = "success"
    message: str = "Image edited successfully."

    model_config = {"from_attributes": True}


class ApproveProjectRequest(BaseModel):
    """Request body for POST /editor/approve."""

    project_id: str = Field(..., description="UUID of the project to approve.")


class ApproveProjectResponse(BaseModel):
    """Response body for POST /editor/approve."""

    project_id: str
    status: str = "approved"
    message: str = "Design approved successfully. Ready for 3D generation."

    model_config = {"from_attributes": True}


# ─────────────────────────────────────────────────────────────────────────────
# 3D Model Generation
# ─────────────────────────────────────────────────────────────────────────────

class Generate3DRequest(BaseModel):
    """
    Request body for POST /viewer/generate3d.

    Attributes
    ----------
    project_id : str
        UUID of the project (must have an edited image ready).
    image_id : str, optional
        Direct UUID of the image to convert to 3D (overrides project).

    Example JSON
    ------------
    {
        "project_id": "a1b2c3d4-..."
    }
    """

    project_id: str = Field(
        ...,
        description="UUID of the project to generate a 3D model for.",
        examples=["a1b2c3d4-58cc-4372-a567-0e02b2c3d479"],
    )
    image_id: Optional[str] = Field(
        default=None,
        description="Optional: directly specify an image UUID.",
    )


class Generate3DResponse(BaseModel):
    """
    Response body for POST /viewer/generate3d.

    Attributes
    ----------
    project_id : str
        UUID of the project.
    model : str
        Relative path to the .glb file in storage/models3d/.
    status : str
        ``"success"`` on success.
    message : str
        Human-readable result message.

    Example JSON
    ------------
    {
        "project_id": "a1b2c3d4-...",
        "model": "storage/models3d/sample.glb",
        "status": "success",
        "message": "3D model generated successfully."
    }
    """

    project_id: str
    model: str
    status: str = "success"
    message: str = "3D model generated successfully."

    model_config = {"from_attributes": True}
