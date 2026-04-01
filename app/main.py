import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.router import api_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Backend Core for SmartSpare AI Factory Operations"
)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_PREFIX)


@app.get("/health", tags=["System Operations"])
async def health_check():
    """Provides a simple ping to verify the web server is online."""
    return {
        "status": "operational",
        "service": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT
    }

logger.info(f"Successfully booted {settings.PROJECT_NAME} in {settings.ENVIRONMENT} mode.")