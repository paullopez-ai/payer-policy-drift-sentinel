from __future__ import annotations

from fastapi import APIRouter

from src.config.settings import settings

router = APIRouter()


@router.get("/health")
async def health() -> dict:
    return {
        "status": "ok",
        "mode": "mock" if settings.is_mock else "live",
        "app_env": settings.app_env,
        "dependencies": {
            "snowflake": "mock" if settings.is_mock else "live",
            "databricks": "mock" if settings.is_mock else "live",
            "azure_openai": "mock" if settings.is_mock else "live",
        },
    }
