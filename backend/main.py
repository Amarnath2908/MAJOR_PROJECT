"""
main.py — DesignVerse AI Backend Entry Point
=============================================
This is the root of the FastAPI application. It:
  - Creates the app instance with OpenAPI metadata
  - Registers all API routers
  - Mounts static file directories for uploads, edits, models, etc.
  - Configures CORS middleware for cross-origin requests
  - Registers global exception handlers
  - Initialises the SQLite database on startup
  - Runs Uvicorn when executed directly
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# ── Internal imports ──────────────────────────────────────────────────────────
from config import settings
from database.database import Base, engine
from middleware.exception_handler import register_exception_handlers
from utils.logger import get_logger

# ── Route modules ─────────────────────────────────────────────────────────────
from api.auth import router as auth_router
from api.upload import get_image_file, router as upload_router
from api.analysis import router as analysis_router
from api.editor import router as editor_router
from api.viewer import router as viewer_router
from api.history import router as history_router

# ── Storage path setup ────────────────────────────────────────────────────────
from utils.file_utils import ensure_storage_dirs

logger = get_logger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Application Factory
# ─────────────────────────────────────────────────────────────────────────────

def create_application() -> FastAPI:
    """
    Factory function that builds and configures the FastAPI application.

    Separating creation into a factory makes unit-testing easier —
    tests can call create_application() to get a fresh app without
    running the global startup side-effects.

    Returns
    -------
    FastAPI
        A fully configured FastAPI application instance.
    """

    # ── 1. App Instance ───────────────────────────────────────────────────────
    application = FastAPI(
        title=settings.APP_NAME,
        description=(
            "DesignVerse AI — an AI-powered interior/exterior design platform. "
            "Upload a room or object image, analyse it, customise via natural "
            "language prompts, and generate 3-D models."
        ),
        version=settings.APP_VERSION,
        docs_url="/docs",          # Swagger UI
        redoc_url="/redoc",        # ReDoc UI
        openapi_url="/openapi.json",
    )

    # ── 2. CORS Middleware ────────────────────────────────────────────────────
    # Allows the React / Next.js frontend (running on a different port) to
    # make requests to this API during development.
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,   # from .env
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── 3. Global Exception Handlers ─────────────────────────────────────────
    # All unhandled errors (404, 401, 422, 500, etc.) are caught here so
    # every error response follows the same JSON envelope.
    register_exception_handlers(application)

    # ── 4. Static File Mounts ─────────────────────────────────────────────────
    # The 'storage' directory is served as static files so the frontend can
    # reference images and 3-D model files by URL directly.
    # e.g.  GET /storage/uploads/abc123.jpg
    application.mount(
        "/storage",
        StaticFiles(directory=str(settings.STORAGE_BASE_DIR)),
        name="storage",
    )

    # ── 5. API Routers ────────────────────────────────────────────────────────
    # Each router is registered with a URL prefix and an OpenAPI tag so the
    # Swagger UI groups endpoints logically.
    application.include_router(auth_router,     prefix="/auth",     tags=["Authentication"])
    application.include_router(upload_router,   prefix="/upload",   tags=["Upload"])
    application.include_router(analysis_router, prefix="/analysis", tags=["Analysis"])
    application.include_router(editor_router,   prefix="/editor",   tags=["Editor"])
    application.include_router(viewer_router,   prefix="/viewer",   tags=["3D Viewer"])
    application.include_router(history_router,  prefix="/history",  tags=["History"])

    # Direct top-level endpoint for PostgreSQL BYTEA image retrieval
    application.get(
        "/images/{image_id}",
        tags=["Images"],
        summary="Retrieve binary image from PostgreSQL BYTEA",
        description="Streams raw image binary stored in PostgreSQL with original MIME type.",
    )(get_image_file)

    logger.info("DesignVerse AI application created successfully.")
    return application


# ─────────────────────────────────────────────────────────────────────────────
# Startup / Shutdown Events
# ─────────────────────────────────────────────────────────────────────────────

app = create_application()


@app.on_event("startup")
async def on_startup() -> None:
    """
    Runs once when the server boots.

    Actions
    -------
    1. Create all SQLAlchemy tables (if they don't exist) against the SQLite db.
    2. Ensure every required storage sub-directory is present on disk.
    3. Pre-warm GroundingDINO and SAM models (loads weights once into memory).
    """
    logger.info("=== DesignVerse AI — Server Starting ===")

    # Create DB tables defined in database/models.py
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables ensured.")

    # Create storage sub-folders: uploads/, edited/, masks/, depth/, models3d/, thumbnails/
    ensure_storage_dirs()
    logger.info("Storage directories ensured.")

    logger.info("=== Server Ready ===")

    # Pre-warm AI models in background thread so the server boots immediately
    # and opens port 8000 without freezing during heavy weight loading on CPU
    import threading

    def _warmup_worker():
        try:
            from ai.grounding_dino import _get_dino_model
            _get_dino_model()
            logger.info("GroundingDINO model pre-warmed successfully.")
        except Exception as exc:
            logger.warning("GroundingDINO pre-warm skipped: %s", exc)

        try:
            from ai.sam import _get_sam_predictor
            _get_sam_predictor()
            logger.info("SAM model pre-warmed successfully.")
        except Exception as exc:
            logger.warning("SAM pre-warm skipped: %s", exc)

    threading.Thread(target=_warmup_worker, daemon=True, name="ModelWarmupWorker").start()


@app.on_event("shutdown")
async def on_shutdown() -> None:
    """
    Runs once when the server shuts down gracefully.
    Use this hook for cleanup: closing DB connections, flushing queues, etc.
    """
    logger.info("=== DesignVerse AI — Server Shutting Down ===")


# ─────────────────────────────────────────────────────────────────────────────
# Root Health-Check Endpoint
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/", tags=["Health"])
async def root() -> dict:
    """
    Health-check endpoint.

    Returns
    -------
    dict
        A simple JSON response confirming the API is alive.

    Example
    -------
    GET /
    → {"status": "ok", "message": "DesignVerse AI API is running.", "version": "1.0.0"}
    """
    return {
        "status": "ok",
        "message": f"{settings.APP_NAME} API is running.",
        "version": settings.APP_VERSION,
    }


@app.get("/health", tags=["Health"])
async def health_check() -> dict:
    """
    Detailed health-check endpoint suitable for load-balancer probes.

    Returns
    -------
    dict
        Service name, version, and current health state.
    """
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "healthy",
    }


# ─────────────────────────────────────────────────────────────────────────────
# Dev Server Entry Point
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    """
    Run directly with:
        python main.py

    Or via Uvicorn CLI:
        uvicorn main:app --reload --host 0.0.0.0 --port 8000
    """
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,   # hot-reload in development
        log_level="info",
    )
