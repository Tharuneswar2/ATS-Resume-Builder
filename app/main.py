"""
AI Resume Generator — FastAPI Application Entry Point.

Initialises the app, mounts routers, and manages the MongoDB lifecycle.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import connect_to_mongo, close_mongo_connection
from app.api import profiles, resumes, jd, auth

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Lifespan — connect to / disconnect from Mongo on startup/shutdown
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting AI Resume Generator v%s", settings.VERSION)
    await connect_to_mongo()
    yield
    await close_mongo_connection()
    logger.info("Shutdown complete.")


# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Production-grade backend for generating AI-optimized, ATS-friendly PDF resumes.",
    version=settings.VERSION,
    lifespan=lifespan,
)

# CORS must allow credentials for HttpOnly cookies to work
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["Authentication"])
app.include_router(profiles.router, prefix=f"{settings.API_V1_STR}/profiles", tags=["Profiles"])
app.include_router(resumes.router, prefix=f"{settings.API_V1_STR}/resume", tags=["Resume"])
app.include_router(jd.router, prefix=f"{settings.API_V1_STR}/jd", tags=["Job Description"])


# ---------------------------------------------------------------------------
# Health & root
# ---------------------------------------------------------------------------
@app.get("/health", tags=["Health"])
async def health_check():
    """Basic liveness probe."""
    return {"status": "ok"}


@app.get("/", tags=["Health"])
async def root():
    """Welcome landing for the API root."""
    return {
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs": "/docs",
    }