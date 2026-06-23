"""Aggregate API v1 router."""

from fastapi import APIRouter

from app.api.v1 import (
    activity,
    agents,
    auth,
    businesses,
    decisions,
    goals,
    integrations,
    metrics,
    tasks,
    users,
)

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(businesses.router, prefix="/businesses", tags=["businesses"])
api_router.include_router(goals.router, prefix="/businesses", tags=["goals"])
api_router.include_router(agents.router, tags=["agents"])
api_router.include_router(decisions.router, prefix="/businesses", tags=["decisions"])
api_router.include_router(tasks.router, prefix="/businesses", tags=["tasks"])
api_router.include_router(metrics.router, prefix="/businesses", tags=["metrics"])
api_router.include_router(integrations.router, prefix="/businesses", tags=["integrations"])
api_router.include_router(activity.router, prefix="/businesses", tags=["activity"])
