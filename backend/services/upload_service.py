"""
services/upload_service.py — Image Upload Business Logic
=========================================================
Handles everything related to receiving and persisting user-uploaded images.

Responsibilities
----------------
- Validate MIME type against the allowed list.
- Validate file size (in MB) against the configured max.
- Save the file to storage/uploads/ via file_utils.
- Extract image dimensions using Pillow.
- Create an UploadedImage record in the database.
- Return a structured UploadResponse.

Functions
---------
validate_file_type()     Raise 415 if MIME type is not allowed.
validate_file_size()     Raise 413 if file exceeds max size.
process_upload()         Main entry point called by the upload route.
get_image_by_id()        Retrieve an UploadedImage record by UUID.
"""

import io
from pathlib import Path
from typing import Optional

from fastapi import HTTPException, UploadFile, status
from PIL import Image
from sqlalchemy.orm import Session

from config import settings
from database.models import UploadedImage, User
from schemas.upload_schema import ImageMetadataResponse, UploadResponse
from utils.file_utils import (
    generate_filename,
    get_file_size_mb,
    save_upload_file,
)
from utils.helpers import format_datetime, generate_uuid
from utils.logger import get_logger

logger = get_logger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Validation Helpers
# ─────────────────────────────────────────────────────────────────────────────

def validate_file_type(upload_file: UploadFile) -> str:
    """
    Validate that the uploaded file's content type is an allowed image MIME type.

    Parameters
    ----------
    upload_file : UploadFile
        The incoming file object from FastAPI.

    Returns
    -------
    str
        The validated MIME type string (e.g. ``"image/jpeg"``).

    Raises
    ------
    HTTPException (415 Unsupported Media Type)
        If the MIME type is not in ``settings.ALLOWED_IMAGE_TYPES``.
    """
    content_type = upload_file.content_type or ""

    if content_type not in settings.ALLOWED_IMAGE_TYPES:
        logger.warning(
            "Rejected upload with unsupported MIME type: %s", content_type
        )
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=(
                f"File type '{content_type}' is not supported. "
                f"Allowed types: {', '.join(settings.ALLOWED_IMAGE_TYPES)}"
            ),
        )
    return content_type


async def validate_file_size(upload_file: UploadFile) -> bytes:
    """
    Read the entire file into memory and validate its size.

    Parameters
    ----------
    upload_file : UploadFile
        The incoming file from FastAPI.

    Returns
    -------
    bytes
        The raw file contents (already read — do not read again).

    Raises
    ------
    HTTPException (413 Request Entity Too Large)
        If the file size exceeds ``settings.MAX_UPLOAD_SIZE_MB``.
    """
    contents = await upload_file.read()
    size_mb = len(contents) / (1024 * 1024)
    max_mb = settings.MAX_UPLOAD_SIZE_MB

    if size_mb > max_mb:
        logger.warning(
            "Rejected upload: %.2f MB exceeds limit of %d MB.", size_mb, max_mb
        )
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size ({size_mb:.2f} MB) exceeds the maximum allowed size of {max_mb} MB.",
        )

    logger.debug("File size validated: %.2f MB", size_mb)
    return contents


def extract_image_dimensions(file_bytes: bytes) -> tuple[Optional[int], Optional[int]]:
    """
    Extract the pixel dimensions of an image using Pillow.

    Parameters
    ----------
    file_bytes : bytes
        Raw bytes of the uploaded image file.

    Returns
    -------
    tuple[int or None, int or None]
        A ``(width, height)`` tuple, or ``(None, None)`` if extraction fails.
    """
    try:
        with Image.open(io.BytesIO(file_bytes)) as img:
            width, height = img.size
            logger.debug("Image dimensions: %dx%d", width, height)
            return width, height
    except Exception as exc:
        logger.warning("Could not extract image dimensions: %s", exc)
        return None, None


# ─────────────────────────────────────────────────────────────────────────────
# Main Upload Handler
# ─────────────────────────────────────────────────────────────────────────────

async def process_upload(
    db: Session,
    upload_file: UploadFile,
    current_user: User,
) -> UploadResponse:
    """
    Full upload pipeline for a single image file.

    Steps
    -----
    1. Validate MIME type → 415 if invalid.
    2. Read file into memory and validate size → 413 if too large.
    3. Extract image dimensions with Pillow.
    4. Generate a UUID-based stored filename.
    5. Write the file to ``storage/uploads/``.
    6. Create an ``UploadedImage`` database record.
    7. Return an ``UploadResponse`` with all metadata.

    Parameters
    ----------
    db : Session
        Active SQLAlchemy database session.
    upload_file : UploadFile
        The raw uploaded file from the HTTP request.
    current_user : User
        The authenticated user who is uploading the image.

    Returns
    -------
    UploadResponse
        Structured response containing image_id, path, dimensions, etc.

    Raises
    ------
    HTTPException (415)
        If file type is not supported.
    HTTPException (413)
        If file is too large.
    HTTPException (500)
        If file saving or database insertion fails.
    """
    original_filename = upload_file.filename or "upload.jpg"

    # ── Step 1: Validate MIME type ────────────────────────────────────────────
    mime_type = validate_file_type(upload_file)

    # ── Step 2: Read & validate size ─────────────────────────────────────────
    file_bytes = await validate_file_size(upload_file)
    size_mb = round(len(file_bytes) / (1024 * 1024), 2)

    # ── Step 3: Extract dimensions ────────────────────────────────────────────
    width, height = extract_image_dimensions(file_bytes)

    # ── Step 4: Generate unique stored filename ───────────────────────────────
    stored_filename = generate_filename(original_filename)
    dest_path = settings.UPLOADS_DIR / stored_filename

    # ── Step 5: Write file to disk ────────────────────────────────────────────
    try:
        dest_path.write_bytes(file_bytes)
        logger.info("File saved: %s", dest_path)
    except Exception as exc:
        logger.error("Failed to write file to disk: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save the uploaded file. Please try again.",
        ) from exc

    # ── Step 6: Generate UUID & build relative path for DB & API response ─────
    image_id = generate_uuid()
    relative_path = f"upload/images/{image_id}"

    # ── Step 7: Create DB record with BYTEA binary data in PostgreSQL ────────
    image_record = UploadedImage(
        id=image_id,
        user_id=current_user.id,
        original_filename=original_filename,
        stored_filename=stored_filename,
        file_path=relative_path,
        file_size_mb=size_mb,
        mime_type=mime_type,
        width=width,
        height=height,
        image_data=file_bytes,   # Stored directly as PostgreSQL BYTEA
        status="uploaded",
    )

    try:
        db.add(image_record)
        db.commit()
        db.refresh(image_record)
        logger.info(
            "UploadedImage record created in PostgreSQL: id=%s user=%s bytes=%d",
            image_id,
            current_user.username,
            len(file_bytes),
        )
    except Exception as exc:
        db.rollback()
        # Clean up the saved disk cache if DB insertion fails
        if dest_path.exists():
            dest_path.unlink()
        logger.error("DB insert failed for upload: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to record the upload. Please try again.",
        ) from exc

    # ── Step 8: Return response ───────────────────────────────────────────────
    return UploadResponse(
        image_id=image_id,
        image_path=relative_path,
        original_filename=original_filename,
        file_size_mb=size_mb,
        width=width,
        height=height,
        mime_type=mime_type,
        status="uploaded",
        message="Image uploaded successfully.",
    )


# ─────────────────────────────────────────────────────────────────────────────
# Lookup Helper
# ─────────────────────────────────────────────────────────────────────────────

def get_image_by_id(
    db: Session,
    image_id: str,
    user_id: Optional[str] = None,
) -> UploadedImage:
    """
    Retrieve an UploadedImage record by its UUID.

    Optionally filters by user_id to enforce ownership (so user A
    cannot access user B's images).

    Parameters
    ----------
    db : Session
        Active SQLAlchemy database session.
    image_id : str
        UUID of the UploadedImage to retrieve.
    user_id : str, optional
        If provided, the record must belong to this user.

    Returns
    -------
    UploadedImage
        The matching database record.

    Raises
    ------
    HTTPException (404 Not Found)
        If no record with this UUID exists (or belongs to the user).
    """
    query = db.query(UploadedImage).filter(UploadedImage.id == image_id)

    if user_id:
        query = query.filter(UploadedImage.user_id == user_id)

    image = query.first()

    if image is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Image with id '{image_id}' was not found.",
        )

    return image


def get_image_metadata(
    db: Session,
    image_id: str,
    current_user: User,
) -> ImageMetadataResponse:
    """
    Return metadata for a single image, enforcing ownership.

    Parameters
    ----------
    db : Session
        Active SQLAlchemy database session.
    image_id : str
        UUID of the image.
    current_user : User
        The requesting authenticated user.

    Returns
    -------
    ImageMetadataResponse
        Structured image metadata.
    """
    image = get_image_by_id(db, image_id, user_id=current_user.id)

    return ImageMetadataResponse(
        id=image.id,
        user_id=image.user_id,
        original_filename=image.original_filename,
        file_path=image.file_path,
        file_size_mb=image.file_size_mb,
        mime_type=image.mime_type,
        width=image.width,
        height=image.height,
        status=image.status,
        created_at=format_datetime(image.created_at),
    )


def ensure_image_on_disk(image: UploadedImage) -> Path:
    """
    Ensure the image file exists on disk, re-hydrating from PostgreSQL BYTEA if missing.

    This ensures that downstream AI modules or image tools expecting a file path
    continue to work even if local disk storage was cleared or restarted.
    PostgreSQL image_data is the definitive source of truth.
    """
    disk_path = settings.UPLOADS_DIR / image.stored_filename
    if not disk_path.exists():
        if image.image_data:
            disk_path.parent.mkdir(parents=True, exist_ok=True)
            disk_path.write_bytes(image.image_data)
            logger.info("Re-hydrated image from PostgreSQL BYTEA to disk: %s", disk_path)
        else:
            logger.error("Image record %s has no binary data in PostgreSQL.", image.id)
    return disk_path


def get_image_binary(
    db: Session,
    image_id: str,
    user_id: Optional[str] = None,
) -> tuple[bytes, str, str]:
    """
    Retrieve raw image bytes and metadata directly from PostgreSQL BYTEA storage.

    Parameters
    ----------
    db : Session
        Active database session.
    image_id : str
        UUID of the image.
    user_id : str, optional
        User ID to verify ownership. If None, ownership is not restricted.

    Returns
    -------
    tuple[bytes, str, str]
        (image_bytes, mime_type, filename)
    """
    image = get_image_by_id(db, image_id, user_id=user_id)
    if not image.image_data:
        # Check if file exists on disk and backfill PostgreSQL
        disk_path = settings.UPLOADS_DIR / image.stored_filename
        if disk_path.exists():
            image.image_data = disk_path.read_bytes()
            db.commit()
            logger.info("Backfilled image_data in PostgreSQL from disk for id=%s", image.id)
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Image binary data not found in database.",
            )

    mime_type = image.mime_type or "image/jpeg"
    return image.image_data, mime_type, image.original_filename

