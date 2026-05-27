from fastapi import APIRouter

from app.api.v1 import auth, community, dataset, health, profile

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(profile.router, prefix="/profile", tags=["profile"])
api_router.include_router(community.router, prefix="/community", tags=["community"])
api_router.include_router(dataset.router, prefix="/dataset", tags=["dataset"])
