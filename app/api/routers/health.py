from fastapi import APIRouter

from app.core.config import settings
from app.schemas.common import success_response

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check() -> dict:
    """Liveness probe for deployment and local development."""
    return success_response(
        data={
            "status": "ok",
            "environment": settings.environment,
            "api_version": "v1",
        },
        message="ConceptMRI backend is running.",
    )
