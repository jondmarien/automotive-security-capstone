from fastapi import APIRouter

from .endpoints import health as health_endpoints

api_router = APIRouter()

api_router.include_router(
    health_endpoints.router,
    prefix="/health",
    tags=["health"],
)
