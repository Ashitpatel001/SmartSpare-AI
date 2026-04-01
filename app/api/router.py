from fastapi import APIRouter
from app.api.intelligence.router import router as intelligence_router 
from app.api.warehouse import inventory
from app.api.identity import auth

api_router = APIRouter()

api_router.include_router(
    auth.router,
    prefix="/identity",
    tags=["Identity & Access Management"]
)

api_router.include_router(
    intelligence_router,
    prefix="/intelligence",
    tags=["Artificial Intelligence Engine"]
)


api_router.include_router(
    inventory.router,
    prefix="/warehouse",
    tags=["Warehouse & Inventory Operations"]
)

