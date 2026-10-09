"""
config.py — Centralised Application Configuration
===================================================
All configuration values are loaded from the '.env' file using
python-dotenv and Pydantic's BaseSettings.  Every module in the
project imports the singleton 'settings' object from here — never
reads os.environ directly.

Pydantic's BaseSettings:
  • Reads values from the environment / .env automatically.
  • Type-validates each field (raises a clear error if a required
    variable is missing or has the wrong type).
  • Makes the config self-documenting through field descriptions.
"""

from pathlib import Path
from typing import List, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


# ─────────────────────────────────────────────────────────────────────────────
# Path Constants
# ─────────────────────────────────────────────────────────────────────────────

# Resolve the directory that THIS file lives in (backend/)
BASE_DIR: Path = Path(__file__).resolve().parent

# The root storage directory lives at backend/storage/
STORAGE_DIR: Path = BASE_DIR / "storage"


# ─────────────────────────────────────────────────────────────────────────────
# Settings Model
# ─────────────────────────────────────────────────────────────────────────────

class Settings(BaseSettings):
    """
    Application-wide settings loaded from the '.env' file.

    Every attribute here corresponds to an environment variable.
    Pydantic will raise a ValidationError on startup if a required
    variable is missing, preventing silent mis-configuration.

    Attributes
    ----------
    APP_NAME : str
        Human-readable product name shown in OpenAPI docs.
    APP_VERSION : str
        Semantic version of the API.
    DEBUG : bool
        Enables Uvicorn hot-reload and verbose logging in development.
    HOST : str
        Interface address the Uvicorn server binds to.
    PORT : int
        TCP port the Uvicorn server listens on.
    SECRET_KEY : str
        Secret used to sign JWT tokens.  MUST be changed in production.
    ALGORITHM : str
        JWT signing algorithm (e.g. 'HS256').
    ACCESS_TOKEN_EXPIRE_MINUTES : int
        How long (minutes) an issued access token remains valid.
    DATABASE_URL : str
        SQLAlchemy database connection string.
    STORAGE_BASE_DIR : Path
        Root directory for all file storage sub-folders.
    ALLOWED_ORIGINS : List[str]
        CORS — list of frontend origins permitted to call this API.
    MAX_UPLOAD_SIZE_MB : int
        Maximum allowed file upload size in megabytes.
    ALLOWED_IMAGE_TYPES : List[str]
        MIME types accepted by the upload endpoint.
    """

    # ── App Identity ──────────────────────────────────────────────────────────
    APP_NAME: str = "DesignVerse AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # ── Server ────────────────────────────────────────────────────────────────
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # ── Security / JWT ────────────────────────────────────────────────────────
    SECRET_KEY: str = "changeme-super-secret-key-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24   # 24 hours

    # ── Database ──────────────────────────────────────────────────────────────
    DATABASE_URL: str = "postgresql+psycopg://postgres:admin123@localhost:5432/designverse"

    # ── Storage ───────────────────────────────────────────────────────────────
    STORAGE_BASE_DIR: Path = STORAGE_DIR

    # Sub-folder paths (derived; not read from .env)
    UPLOADS_DIR: Path = STORAGE_DIR / "uploads"
    EDITED_DIR: Path = STORAGE_DIR / "edited"
    MASKS_DIR: Path = STORAGE_DIR / "masks"
    DEPTH_DIR: Path = STORAGE_DIR / "depth"
    MODELS3D_DIR: Path = STORAGE_DIR / "models3d"
    THUMBNAILS_DIR: Path = STORAGE_DIR / "thumbnails"

    # ── CORS ──────────────────────────────────────────────────────────────────
    # Comma-separated in .env: ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]

    # ── Upload Validation ─────────────────────────────────────────────────────
    MAX_UPLOAD_SIZE_MB: int = 20
    ALLOWED_IMAGE_TYPES: List[str] = [
        "image/jpeg",
        "image/png",
        "image/webp",
        "image/bmp",
        "image/tiff",
    ]

    # ── AI Models (GroundingDINO + SAM) ───────────────────────────────────────
    # Set these via environment variables in .env (see backend/.env.example).
    # They are Optional so the server can boot without AI weights installed;
    # the AI endpoints will return a 503 if they are not configured.
    GROUNDING_DINO_ROOT: Optional[Path] = None
    GROUNDING_DINO_CONFIG_PATH: Optional[Path] = None
    GROUNDING_DINO_CHECKPOINT_PATH: Optional[Path] = None
    SAM_CHECKPOINT_PATH: Optional[Path] = None
    SAM_MODEL_TYPE: str = "vit_b"
    DEVICE: str = "cpu"
    GROUNDING_DINO_BOX_THRESHOLD: float = 0.30
    GROUNDING_DINO_TEXT_THRESHOLD: float = 0.25


    # ── Pydantic Settings Config ──────────────────────────────────────────────
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),   # Load from backend/.env
        env_file_encoding="utf-8",
        case_sensitive=True,               # Env vars must match case exactly
        extra="ignore",                    # Silently ignore unknown env vars
    )


# ─────────────────────────────────────────────────────────────────────────────
# Singleton Instance
# ─────────────────────────────────────────────────────────────────────────────

settings = Settings()
"""
Module-level singleton imported by every other module::

    from config import settings

    print(settings.APP_NAME)        # "DesignVerse AI"
    print(settings.DATABASE_URL)    # "sqlite:///...designverse.db"
"""
