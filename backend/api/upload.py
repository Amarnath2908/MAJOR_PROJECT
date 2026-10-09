"""
api/upload.py — Image Upload API Routes
=========================================
Defines HTTP endpoints for image uploading and retrieval.
All business logic delegates to upload_service.

Endpoints
---------
POST /upload/          → Upload a new image file.
GET  /upload/{image_id} → Retrieve metadata for an uploaded image.
"""

from typing import Optional

from fastapi import APIRouter, Depends, File, Query, Response, UploadFile, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from database.database import get_db
from database.models import User
from middleware.auth import decode_access_token, get_current_user
from schemas.upload_schema import ImageMetadataResponse, UploadResponse
from services import upload_service
from utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()
optional_bearer = HTTPBearer(auto_error=False)


def authenticate_image_access(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(optional_bearer),
    token: Optional[str] = Query(None, description="JWT token for direct <img> tag embedding"),
    db: Session = Depends(get_db),
) -> User:
    """
    Authenticate image retrieval requests via Bearer header or ?token= query parameter.
    Enforces that only authenticated users can access uploaded image binaries.
    """
    raw_token = None
    if credentials and credentials.credentials:
        raw_token = credentials.credentials
    elif token:
        raw_token = token

    if not raw_token:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token required to view this image.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = decode_access_token(raw_token)
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or account is deactivated.",
        )
    return user


# ─────────────────────────────────────────────────────────────────────────────
# Upload Image
# ─────────────────────────────────────────────────────────────────────────────

@router.post(
    "/",
    response_model=UploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload an image",
    description=(
        "Upload an image file (JPEG, PNG, WEBP, BMP, TIFF). "
        "Returns a unique image_id and storage path for use in subsequent "
        "analysis and editing requests. Max file size: 20 MB."
    ),
)
async def upload_image(
    file: UploadFile = File(..., description="Image file to upload."),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UploadResponse:
    """
    Accept and store an uploaded image file.

    The endpoint is ``async`` because saving large files to disk
    is an I/O-bound operation that benefits from async handling.

    Parameters
    ----------
    file : UploadFile
        The multipart image file from the request.
    current_user : User
        Authenticated user from JWT Bearer token.
    db : Session
        Injected database session.

    Returns
    -------
    UploadResponse
        image_id, image_path, dimensions, MIME type, and status.

    Raises
    ------
    HTTPException 415
        If the file type is not an accepted image format.
    HTTPException 413
        If the file exceeds the maximum size limit.
    HTTPException 401
        If no valid Bearer token is provided.
    """
    logger.info(
        "Upload request from user=%s filename='%s'",
        current_user.username,
        file.filename,
    )
    return await upload_service.process_upload(db, file, current_user)


# ─────────────────────────────────────────────────────────────────────────────
# Get Image Metadata
# ─────────────────────────────────────────────────────────────────────────────

@router.get(
    "/{image_id}",
    response_model=ImageMetadataResponse,
    status_code=status.HTTP_200_OK,
    summary="Get uploaded image metadata",
    description=(
        "Retrieve metadata for a specific uploaded image by its UUID. "
        "Only the authenticated owner can access their own images."
    ),
)
def get_image(
    image_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ImageMetadataResponse:
    """
    Retrieve metadata for a previously uploaded image.

    Parameters
    ----------
    image_id : str
        UUID of the uploaded image.
    current_user : User
        Authenticated user — must be the image owner.
    db : Session
        Injected database session.

    Returns
    -------
    ImageMetadataResponse
        All metadata: path, dimensions, MIME type, status, timestamp.

    Raises
    ------
    HTTPException 404
        If the image is not found or doesn't belong to the current user.
    HTTPException 401
        If no valid Bearer token is provided.
    """
    return upload_service.get_image_metadata(db, image_id, current_user)


# ─────────────────────────────────────────────────────────────────────────────
# Stream Uploaded Image from PostgreSQL BYTEA
# ─────────────────────────────────────────────────────────────────────────────

@router.get(
    "/images/{image_id}",
    summary="Retrieve binary image from PostgreSQL BYTEA",
    description="Streams the raw image binary stored in PostgreSQL with the original MIME type.",
)
@router.get(
    "/{image_id}/file",
    summary="Retrieve binary image from PostgreSQL BYTEA (alias)",
)
def get_image_file(
    image_id: str,
    current_user: User = Depends(authenticate_image_access),
    db: Session = Depends(get_db),
) -> Response:
    """
    Read image binary data directly from PostgreSQL BYTEA and return HTTP response.
    Enforces that only the authenticated owner can access the image.
    """
    image_bytes, mime_type, filename = upload_service.get_image_binary(
        db, image_id, user_id=current_user.id
    )
    return Response(
        content=image_bytes,
        media_type=mime_type,
        headers={
            "Content-Disposition": f'inline; filename="{filename}"',
            "Cache-Control": "private, max-age=3600",
        },
    )

