"""
schemas/upload_schema.py — Upload & Image Pydantic Schemas
===========================================================
Defines request and response shapes for the upload and image endpoints.

Schemas
-------
UploadResponse        → Response from POST /upload.
ImageMetadataResponse → Detailed info about a single uploaded image.
"""

from typing import Optional

from pydantic import BaseModel, Field


class UploadResponse(BaseModel):
    """
    Response body returned by POST /upload.

    Attributes
    ----------
    image_id : str
        UUID of the newly created UploadedImage record.
    image_path : str
        Relative URL path to access the image, e.g.
        ``"storage/uploads/f47ac10b.jpg"``.
    original_filename : str
        The original file name provided by the user.
    file_size_mb : float
        Size of the uploaded file in megabytes.
    width : int or None
        Image width in pixels.
    height : int or None
        Image height in pixels.
    mime_type : str or None
        Detected MIME type (e.g. ``"image/jpeg"``).
    status : str
        Always ``"uploaded"`` on successful response.
    message : str
        Human-readable confirmation message.

    Example JSON
    ------------
    {
        "image_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
        "image_path": "storage/uploads/f47ac10b.jpg",
        "original_filename": "living_room.jpg",
        "file_size_mb": 2.45,
        "width": 1920,
        "height": 1080,
        "mime_type": "image/jpeg",
        "status": "uploaded",
        "message": "Image uploaded successfully."
    }
    """

    image_id: str
    image_path: str
    original_filename: str
    file_size_mb: float = Field(default=0.0, description="File size in MB.")
    width: Optional[int] = None
    height: Optional[int] = None
    mime_type: Optional[str] = None
    status: str = "uploaded"
    message: str = "Image uploaded successfully."

    model_config = {"from_attributes": True}


class ImageMetadataResponse(BaseModel):
    """
    Detailed metadata about a single uploaded image.

    Returned by GET /upload/{image_id} (if implemented).

    Attributes
    ----------
    id : str
        UUID of the image record.
    user_id : str
        UUID of the owning user.
    original_filename : str
        Original file name.
    file_path : str
        Relative storage path.
    file_size_mb : float
        Size in MB.
    mime_type : str or None
        MIME type.
    width : int or None
        Width in pixels.
    height : int or None
        Height in pixels.
    status : str
        Current processing status.
    created_at : str or None
        ISO-8601 upload timestamp.
    """

    id: str
    user_id: str
    original_filename: str
    file_path: str
    file_size_mb: Optional[float] = None
    mime_type: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    status: str
    created_at: Optional[str] = None

    model_config = {"from_attributes": True}
