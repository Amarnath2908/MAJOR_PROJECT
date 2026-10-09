"""
database/models.py — SQLAlchemy ORM Table Definitions
======================================================
Defines every database table as a Python class.  SQLAlchemy maps these
classes to SQL tables automatically.

Tables
------
User           → Stores registered user accounts.
UploadedImage  → Records every image upload with path and status.
Project        → Represents a full design session (upload → edit → 3D).

Relationships
-------------
User ──< UploadedImage   (one user, many uploaded images)
User ──< Project         (one user, many projects)
Project → UploadedImage  (each project references one uploaded image)

All primary keys are UUID strings (not auto-increment integers) so that
IDs can be generated client-side or before DB insertion, and they are
globally unique across distributed systems.
"""

from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    LargeBinary,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from database.database import Base


# ─────────────────────────────────────────────────────────────────────────────
# Helper: UTC-aware default
# ─────────────────────────────────────────────────────────────────────────────

def _utc_now() -> datetime:
    """Return the current UTC datetime (timezone-aware)."""
    return datetime.now(tz=timezone.utc)


# ─────────────────────────────────────────────────────────────────────────────
# User Table
# ─────────────────────────────────────────────────────────────────────────────

class User(Base):
    """
    Represents a registered user account.

    Columns
    -------
    id : str
        UUID primary key generated before insertion.
    username : str
        Unique display name.  Max 50 characters.
    email : str
        Unique email address used for login.
    hashed_password : str
        Bcrypt-hashed password — never store plain text.
    full_name : str
        Optional full name for display purposes.
    is_active : bool
        Whether the account is active.  Defaults to True.
        Set to False to "soft-delete" or suspend an account.
    is_verified : bool
        Email verification flag (for future email-confirm flow).
    created_at : datetime
        Account creation timestamp (UTC).
    updated_at : datetime
        Last modification timestamp (UTC), auto-updated.

    Relationships
    -------------
    images   : List[UploadedImage]
        All images uploaded by this user.
    projects : List[Project]
        All design projects created by this user.
    """

    __tablename__ = "users"

    id: str = Column(String(36), primary_key=True, index=True)
    username: str = Column(String(50), unique=True, nullable=False, index=True)
    email: str = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password: str = Column(String(255), nullable=False)
    full_name: str = Column(String(100), nullable=True)
    is_active: bool = Column(Boolean, default=True, nullable=False)
    is_verified: bool = Column(Boolean, default=False, nullable=False)
    created_at: datetime = Column(
        DateTime(timezone=True), default=_utc_now, nullable=False
    )
    updated_at: datetime = Column(
        DateTime(timezone=True), default=_utc_now, onupdate=_utc_now, nullable=False
    )

    # ── Relationships ─────────────────────────────────────────────────────────
    images = relationship(
        "UploadedImage",
        back_populates="owner",
        cascade="all, delete-orphan",   # Delete images when user is deleted
        lazy="dynamic",
    )
    projects = relationship(
        "Project",
        back_populates="owner",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )

    def __repr__(self) -> str:
        return f"<User id={self.id!r} username={self.username!r}>"


# ─────────────────────────────────────────────────────────────────────────────
# UploadedImage Table
# ─────────────────────────────────────────────────────────────────────────────

class UploadedImage(Base):
    """
    Records every image uploaded by a user.

    Each upload creates one row.  The file is stored in
    ``storage/uploads/`` and the path is stored here.

    Columns
    -------
    id : str
        UUID primary key.
    user_id : str
        Foreign key → users.id
    original_filename : str
        The original file name as provided by the user.
    stored_filename : str
        The UUID-based filename used on disk (collision-resistant).
    file_path : str
        Relative path from the backend root, e.g.
        ``"storage/uploads/f47ac10b.jpg"``.
    file_size_mb : float
        File size in megabytes.
    mime_type : str
        MIME type, e.g. ``"image/jpeg"``.
    width : int
        Image width in pixels (populated after validation).
    height : int
        Image height in pixels.
    status : str
        Processing status: ``"uploaded"`` | ``"analysed"`` | ``"edited"``.
    created_at : datetime
        Upload timestamp (UTC).

    Relationships
    -------------
    owner   : User
        The user who uploaded this image.
    project : Project
        The project that used this image (if any).
    """

    __tablename__ = "uploaded_images"

    id: str = Column(String(36), primary_key=True, index=True)
    user_id: str = Column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    project_id: str = Column(String(36), nullable=True, index=True)
    original_filename: str = Column(String(255), nullable=False)
    stored_filename: str = Column(String(255), nullable=False)
    file_path: str = Column(String(512), nullable=False)
    file_size_mb: float = Column(Float, nullable=True)
    mime_type: str = Column(String(100), nullable=True)
    width: int = Column(Integer, nullable=True)
    height: int = Column(Integer, nullable=True)
    image_data: bytes = Column(LargeBinary, nullable=False)
    status: str = Column(String(50), default="uploaded", nullable=False)
    created_at: datetime = Column(
        DateTime(timezone=True), default=_utc_now, nullable=False, index=True
    )

    # ── Relationships ─────────────────────────────────────────────────────────
    owner = relationship("User", back_populates="images")
    project = relationship(
        "Project",
        foreign_keys="Project.image_id",
        back_populates="source_image",
        uselist=False,   # One image → at most one project
    )

    def __repr__(self) -> str:
        return (
            f"<UploadedImage id={self.id!r} "
            f"filename={self.stored_filename!r} "
            f"status={self.status!r}>"
        )


# ─────────────────────────────────────────────────────────────────────────────
# Project Table
# ─────────────────────────────────────────────────────────────────────────────

class Project(Base):
    """
    Represents a complete design session.

    A Project ties together all stages of the pipeline:
        Upload → Analysis → Edit → 3D Model

    Each stage populates additional columns.  The project starts
    with status='created' and advances through the pipeline.

    Columns
    -------
    id : str
        UUID primary key.
    user_id : str
        Foreign key → users.id
    image_id : str
        Foreign key → uploaded_images.id
    title : str
        Optional user-provided project name.
    prompt : str
        The natural language instruction sent to the editor.
    analysis_result : str
        JSON string of detected objects (from analysis stage).
    edited_image_path : str
        Relative path to the AI-edited image in storage/edited/.
    model_3d_path : str
        Relative path to the generated .glb file in storage/models3d/.
    thumbnail_path : str
        Relative path to the project thumbnail in storage/thumbnails/.
    status : str
        Pipeline state:
          ``"created"`` → ``"analysed"`` → ``"edited"`` → ``"model_ready"``
    created_at : datetime
        Project creation timestamp (UTC).
    updated_at : datetime
        Last update timestamp (UTC), auto-updated.

    Relationships
    -------------
    owner        : User
        The user who owns this project.
    source_image : UploadedImage
        The image this project was built from.
    """

    __tablename__ = "projects"

    id: str = Column(String(36), primary_key=True, index=True)
    user_id: str = Column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    image_id: str = Column(
        String(36), ForeignKey("uploaded_images.id", ondelete="SET NULL"), nullable=True
    )
    title: str = Column(String(200), nullable=True, default="Untitled Project")
    prompt: str = Column(Text, nullable=True)
    target_object: str = Column(String(100), nullable=True)
    analysis_result: str = Column(Text, nullable=True)   # Stored as JSON string
    edited_image_path: str = Column(String(512), nullable=True)
    edited_image_data: bytes = Column(LargeBinary, nullable=True)
    model_3d_path: str = Column(String(512), nullable=True)
    thumbnail_path: str = Column(String(512), nullable=True)
    status: str = Column(String(50), default="created", nullable=False)
    created_at: datetime = Column(
        DateTime(timezone=True), default=_utc_now, nullable=False, index=True
    )
    updated_at: datetime = Column(
        DateTime(timezone=True), default=_utc_now, onupdate=_utc_now, nullable=False
    )

    # ── Relationships ─────────────────────────────────────────────────────────
    owner = relationship("User", back_populates="projects")
    source_image = relationship("UploadedImage", foreign_keys=[image_id], back_populates="project")

    def __repr__(self) -> str:
        return (
            f"<Project id={self.id!r} "
            f"title={self.title!r} "
            f"status={self.status!r}>"
        )
