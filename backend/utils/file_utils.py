"""
utils/file_utils.py — File System & Storage Utilities
======================================================
All file-system operations for the project are centralised here.
No other module should use os.path, shutil, or pathlib directly for
storage purposes — always call these helpers.

This makes it trivial to swap local disk for S3 / GCS later:
only this file needs to change.

Functions
---------
ensure_storage_dirs()   Create all required sub-directories under storage/.
generate_filename()     Build a unique file name from a UUID and extension.
save_upload_file()      Persist a FastAPI UploadFile to disk.
save_bytes()            Write raw bytes to a destination path.
get_file_path()         Resolve the absolute path for a stored file.
delete_file()           Remove a file from disk (silent if missing).
file_exists()           Check whether a file path exists on disk.
get_file_size_mb()      Return a file's size in megabytes.
"""

import shutil
import uuid
from pathlib import Path
from typing import Optional

from fastapi import UploadFile

from config import settings
from utils.logger import get_logger

logger = get_logger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Storage Sub-directory Map
# ─────────────────────────────────────────────────────────────────────────────

STORAGE_SUBDIRS: dict[str, Path] = {
    "uploads":    settings.UPLOADS_DIR,
    "edited":     settings.EDITED_DIR,
    "masks":      settings.MASKS_DIR,
    "depth":      settings.DEPTH_DIR,
    "models3d":   settings.MODELS3D_DIR,
    "thumbnails": settings.THUMBNAILS_DIR,
}
"""
Maps logical bucket names to absolute filesystem paths.
Used by ensure_storage_dirs() and get_file_path().
"""


# ─────────────────────────────────────────────────────────────────────────────
# Directory Setup
# ─────────────────────────────────────────────────────────────────────────────

def ensure_storage_dirs() -> None:
    """
    Create all required storage sub-directories if they do not exist.

    Called once at application startup from main.py's on_startup event.
    Safe to call multiple times — uses mkdir(exist_ok=True).

    Storage layout created:
        backend/storage/
            uploads/       ← original user uploads
            edited/        ← AI-edited images
            masks/         ← segmentation masks
            depth/         ← depth maps
            models3d/      ← generated .glb / .obj 3-D models
            thumbnails/    ← image previews
    """
    settings.STORAGE_BASE_DIR.mkdir(parents=True, exist_ok=True)

    for name, path in STORAGE_SUBDIRS.items():
        path.mkdir(parents=True, exist_ok=True)
        logger.debug("Storage directory ensured: %s", path)

    logger.info("All storage directories are ready.")


# ─────────────────────────────────────────────────────────────────────────────
# Filename Generation
# ─────────────────────────────────────────────────────────────────────────────

def generate_filename(original_filename: str, prefix: str = "") -> str:
    """
    Generate a unique, collision-resistant filename.

    The original file name is discarded to prevent path-traversal attacks
    and filename collisions.  Only the file extension is preserved.

    Parameters
    ----------
    original_filename : str
        The original name of the uploaded file (e.g. ``"photo.jpg"``).
    prefix : str, optional
        Short label prepended to the UUID (e.g. ``"edit"`` → ``"edit_<uuid>.jpg"``).

    Returns
    -------
    str
        A unique filename string (e.g. ``"a1b2c3d4-...-e5f6.jpg"``).

    Examples
    --------
    >>> generate_filename("room.jpg")
    'f47ac10b-58cc-4372-a567-0e02b2c3d479.jpg'

    >>> generate_filename("room.jpg", prefix="thumb")
    'thumb_f47ac10b-58cc-4372-a567-0e02b2c3d479.jpg'
    """
    ext = Path(original_filename).suffix.lower()   # e.g. ".jpg"
    unique_id = str(uuid.uuid4())
    if prefix:
        return f"{prefix}_{unique_id}{ext}"
    return f"{unique_id}{ext}"


# ─────────────────────────────────────────────────────────────────────────────
# Save Files
# ─────────────────────────────────────────────────────────────────────────────

async def save_upload_file(upload_file: UploadFile, bucket: str) -> Path:
    """
    Persist a FastAPI ``UploadFile`` to the specified storage bucket.

    Parameters
    ----------
    upload_file : UploadFile
        The in-memory file received from the HTTP multipart request.
    bucket : str
        Target sub-directory key — one of: ``"uploads"``, ``"edited"``,
        ``"masks"``, ``"depth"``, ``"models3d"``, ``"thumbnails"``.

    Returns
    -------
    Path
        The absolute filesystem path where the file was saved.

    Raises
    ------
    ValueError
        If ``bucket`` is not a recognised sub-directory name.
    IOError
        If writing the file to disk fails.

    Examples
    --------
    >>> path = await save_upload_file(upload_file, "uploads")
    >>> str(path)
    '/...backend/storage/uploads/f47ac10b-....jpg'
    """
    if bucket not in STORAGE_SUBDIRS:
        raise ValueError(
            f"Unknown storage bucket '{bucket}'. "
            f"Valid options: {list(STORAGE_SUBDIRS.keys())}"
        )

    dest_dir = STORAGE_SUBDIRS[bucket]
    filename = generate_filename(upload_file.filename or "file.bin")
    dest_path = dest_dir / filename

    try:
        with dest_path.open("wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
    except Exception as exc:
        logger.error("Failed to save upload file: %s", exc)
        raise IOError(f"Could not write file to disk: {exc}") from exc
    finally:
        await upload_file.close()

    logger.info("Saved upload to: %s", dest_path)
    return dest_path


def save_bytes(data: bytes, bucket: str, filename: str) -> Path:
    """
    Write raw bytes to a storage bucket under the given filename.

    Used by AI services to save processed results (masks, depth maps,
    edited images, etc.) that arrive as byte arrays rather than UploadFile.

    Parameters
    ----------
    data : bytes
        Raw file content to write.
    bucket : str
        Target sub-directory key.
    filename : str
        Desired filename within the bucket (should be pre-generated via
        ``generate_filename()``).

    Returns
    -------
    Path
        The absolute path where the file was written.

    Raises
    ------
    ValueError
        If ``bucket`` is unrecognised.
    """
    if bucket not in STORAGE_SUBDIRS:
        raise ValueError(f"Unknown storage bucket '{bucket}'.")

    dest_path = STORAGE_SUBDIRS[bucket] / filename
    dest_path.write_bytes(data)
    logger.info("Saved bytes (%d B) to: %s", len(data), dest_path)
    return dest_path


# ─────────────────────────────────────────────────────────────────────────────
# Retrieve Files
# ─────────────────────────────────────────────────────────────────────────────

def get_file_path(bucket: str, filename: str) -> Path:
    """
    Resolve the absolute filesystem path for a stored file.

    Parameters
    ----------
    bucket : str
        Storage sub-directory key.
    filename : str
        Name of the file within that bucket.

    Returns
    -------
    Path
        Absolute path to the file.

    Raises
    ------
    ValueError
        If the bucket name is not recognised.
    FileNotFoundError
        If no file with that name exists in the bucket.
    """
    if bucket not in STORAGE_SUBDIRS:
        raise ValueError(f"Unknown storage bucket '{bucket}'.")

    path = STORAGE_SUBDIRS[bucket] / filename

    if not path.exists():
        raise FileNotFoundError(
            f"File '{filename}' not found in bucket '{bucket}'."
        )

    return path


def get_relative_path(absolute_path: Path) -> str:
    """
    Convert an absolute storage path to a relative URL-safe string.

    Example:  /…/backend/storage/uploads/abc.jpg  →  "storage/uploads/abc.jpg"
    This relative path is what gets stored in the database and returned in API
    responses so that the frontend can build a URL: GET /storage/uploads/abc.jpg.

    Parameters
    ----------
    absolute_path : Path
        Absolute path returned by save_upload_file() or save_bytes().

    Returns
    -------
    str
        Path relative to the backend root (starts with ``"storage/"``).
    """
    try:
        return str(absolute_path.relative_to(settings.BASE_DIR if hasattr(settings, 'BASE_DIR') else absolute_path.parent.parent.parent))
    except ValueError:
        # Fallback: return the parts after "storage"
        parts = absolute_path.parts
        try:
            storage_idx = parts.index("storage")
            return "/".join(parts[storage_idx:])
        except ValueError:
            return str(absolute_path)


# ─────────────────────────────────────────────────────────────────────────────
# Delete Files
# ─────────────────────────────────────────────────────────────────────────────

def delete_file(bucket: str, filename: str) -> bool:
    """
    Remove a file from a storage bucket.

    Parameters
    ----------
    bucket : str
        Storage sub-directory key.
    filename : str
        Name of the file to delete.

    Returns
    -------
    bool
        ``True`` if the file was deleted; ``False`` if it did not exist.
    """
    if bucket not in STORAGE_SUBDIRS:
        logger.warning("delete_file: unknown bucket '%s'.", bucket)
        return False

    path = STORAGE_SUBDIRS[bucket] / filename

    if path.exists():
        path.unlink()
        logger.info("Deleted file: %s", path)
        return True

    logger.warning("delete_file: '%s' not found in '%s'.", filename, bucket)
    return False


# ─────────────────────────────────────────────────────────────────────────────
# File Metadata Helpers
# ─────────────────────────────────────────────────────────────────────────────

def file_exists(bucket: str, filename: str) -> bool:
    """
    Check whether a file exists in a storage bucket.

    Parameters
    ----------
    bucket : str
        Storage sub-directory key.
    filename : str
        Name of the file to check.

    Returns
    -------
    bool
        ``True`` if the file exists on disk.
    """
    if bucket not in STORAGE_SUBDIRS:
        return False
    return (STORAGE_SUBDIRS[bucket] / filename).exists()


def get_file_size_mb(path: Path) -> float:
    """
    Return the size of a file in megabytes.

    Parameters
    ----------
    path : Path
        Absolute path to the file.

    Returns
    -------
    float
        File size in MB, rounded to 2 decimal places.
        Returns 0.0 if the file does not exist.
    """
    if not path.exists():
        return 0.0
    size_bytes = path.stat().st_size
    return round(size_bytes / (1024 * 1024), 2)
