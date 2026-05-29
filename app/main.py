import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import settings
from app.core.database import connect_to_mongo, close_mongo_connection



logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s — %(message)s"
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Connect to MongoDB when the app starts, and close the connection when it shuts down."""
    await connect_to_mongo()
    yield
    await close_mongo_connection()
    logger.info("Application shutdown complete.")
    
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


@app.get("/",tags=["Health"])
async def root():
    return {"message": "Welcome to the AI Resume Builder API!"}


@app.get("/health",tags=["Health"])
async def health():
    return {
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs": "/docs",
    }