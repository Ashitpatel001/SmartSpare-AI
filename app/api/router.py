import logging
from fastapi import APIRouter
from app.api.warehouse import inventory
from app.api.warehouse import procurement
from app.api.identity import auth

logger = logging.getLogger(__name__)

api_router = APIRouter()

api_router.include_router(
    auth.router,
    prefix="/identity",
    tags=["Identity & Access Management"]
)

# Intelligence router requires ChromaDB (Docker) and Groq API.
# Wrap in try/except so the server always boots for auth & inventory.
try:
    from app.api.intelligence.router import router as intelligence_router
    api_router.include_router(
        intelligence_router,
        prefix="/intelligence",
        tags=["Artificial Intelligence Engine"]
    )
    logger.info("Intelligence module loaded successfully.")
except Exception as e:
    logger.warning(f"Intelligence module unavailable (ChromaDB/Docker may be offline): {e}")


api_router.include_router(
    inventory.router,
    prefix="/warehouse",
    tags=["Warehouse & Inventory Operations"]
)

api_router.include_router(
    procurement.router,
    prefix="/procurement",
    tags=["Procurement Operations"]
)
