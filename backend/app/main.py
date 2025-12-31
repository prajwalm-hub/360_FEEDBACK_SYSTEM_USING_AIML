from __future__ import annotations
import logging

import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse
from pathlib import Path

from .config import settings
from .database import get_database
from .news_collector import NewsCollector

# Setup logging first
logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))
logger = logging.getLogger(__name__)

# Import API routers
from . import api, auth
try:
    from . import api_quality
    QUALITY_API_AVAILABLE = True
except ImportError:
    QUALITY_API_AVAILABLE = False
    logger.warning("Quality API not available")


app = FastAPI(title=settings.APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Initialize DB and ensure tables exist on startup
@app.on_event("startup")
async def on_startup():
    try:
        # Initialize database tables
        db = get_database()
        if settings.DB_PROVIDER.lower() == "postgres":
            db.create_all()
        logger.info("Database tables initialized successfully")
    except Exception as e:
        logger.exception(f"Failed to initialize database: {e}")
        # Don't crash the app if DB init fails
    
    # Start periodic collector in background (best-effort, non-blocking)
    async def periodic_collect():
        await asyncio.sleep(3)
        db_local = get_database()
        collector = NewsCollector(db_local)
        interval = max(1, int(settings.COLLECT_INTERVAL_MIN)) * 60
        while True:
            try:
                collector.collect_once()
            except Exception:
                logging.exception("Periodic collect failed")
            await asyncio.sleep(interval)
    
    # Pre-build RAG vector store in background (non-blocking)
    async def build_rag_vectorstore():
        await asyncio.sleep(5)  # Wait for system to stabilize
        try:
            logger.info("Pre-building RAG vector store...")
            from .rag_api import get_rag_assistant
            db_local = get_database()
            session = db_local.get_session()
            rag = get_rag_assistant(session)
            if not rag.vectorstore:
                rag.build_vectorstore(days=30, force_rebuild=False)
                logger.info("RAG vector store pre-built successfully")
        except Exception as e:
            logger.warning(f"Could not pre-build RAG vector store: {e}")

    # Enable background tasks
    try:
        asyncio.create_task(periodic_collect())
        asyncio.create_task(build_rag_vectorstore())
        logger.info("Background collector scheduled")
    except RuntimeError as e:
        logger.warning(f"Could not schedule background collector: {e}")


# Include RAG router
try:
    from .rag_api import router as rag_router
    app.include_router(rag_router, prefix=settings.API_PREFIX)
    logger.info("RAG router included (OpenAI GPT-4 enabled)")
except Exception as e:
    logger.warning(f"RAG router failed to import: {e}")
    try:
        from .rag_lightweight import router as rag_router
        app.include_router(rag_router, prefix=settings.API_PREFIX)
        logger.info("RAG router included (fallback)")
    except Exception as e2:
        logger.error(f"All RAG routers failed: {e2}")

# Mount working metrics endpoint FIRST
try:
    from .api_metrics import router as metrics_router
    app.include_router(metrics_router, prefix=settings.API_PREFIX)
    logger.info("Metrics router included")
except Exception as e:
    logger.error(f"Metrics router failed: {e}")

# Mount API router
try:
    from .api import router as api_router
    app.include_router(api_router, prefix=settings.API_PREFIX)
    logger.info("API router included")
except Exception as e:
    logger.error(f"API router failed: {e}")
    try:
        from .api_simple import router as simple_router
        app.include_router(simple_router, prefix=settings.API_PREFIX)
        logger.warning("Using simplified API router")
    except Exception as e2:
        logger.error(f"Simplified API also failed: {e2}")

# Mount Quality/Verification API
if QUALITY_API_AVAILABLE:
    try:
        app.include_router(api_quality.router, prefix=settings.API_PREFIX)
        logger.info("Quality API router included")
    except Exception as e:
        logger.error(f"Quality API router failed: {e}")

# Mount Enhanced Assistant API
try:
    from . import api_assistant
    app.include_router(api_assistant.router, prefix=settings.API_PREFIX)
    logger.info("Enhanced Assistant API router included")
except Exception as e:
    logger.warning(f"Enhanced Assistant API not available: {e}")

"""Serve built frontend (Vite) if available.
If the frontend has been built (npm run build) and the dist directory exists,
mount it at the root path so the SPA is available at '/'. API routes remain
under settings.API_PREFIX and take precedence because they're included before.
"""
try:
    # Resolve project root and dist directory
    app_dir = Path(__file__).resolve().parent
    backend_dir = app_dir.parent
    project_root = backend_dir.parent
    dist_dir = project_root / "frontend" / "dist"

    if dist_dir.exists():
        # Mount static files at root; API is already mounted above and takes precedence
        app.mount("/", StaticFiles(directory=dist_dir, html=True), name="static")
        logger.info(f"Mounted frontend static files from: {dist_dir}")
    else:
        logger.info(f"Frontend 'dist' not found at {dist_dir}; skipping static mount")
except Exception:
    # Don't block backend if static mounting fails
    import logging as _logging
    _logging.exception("Failed to mount frontend static files")


# For `uvicorn app.main:app --reload`
__all__ = ["app"]
