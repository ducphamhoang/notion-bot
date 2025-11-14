"""Notion SDK client wrapper with setup and configuration."""

import asyncio
from typing import Optional

from notion_client import AsyncClient, APIResponseError
from src.config.settings import get_settings

_notion_client: Optional[AsyncClient] = None
_client_lock = asyncio.Lock()


async def get_notion_client() -> AsyncClient:
    """Get Notion client instance, creating if needed."""
    global _notion_client

    if _notion_client is None:
        async with _client_lock:
            if _notion_client is None:
                settings = get_settings()

                _notion_client = AsyncClient(
                    auth=settings.notion_api_key,
                    notion_version=settings.notion_api_version,  # Pass API version from settings
                    # Notion client doesn't support timeout in async version,
                    # but we'll handle this in the rate limiter
                )

    return _notion_client


async def test_notion_connection() -> dict:
    """Test Notion API connectivity."""
    try:
        client = await get_notion_client()
        from src.config.settings import get_settings
        settings = get_settings()

        # API 2025-09-03: Use data_source filter for search
        if settings.notion_api_version >= "2025-09-03":
            result = await client.search(
                filter={"property": "object", "value": "data_source"},
                page_size=1
            )
        else:
            # Older API versions: use database filter or no filter
            result = await client.search(page_size=1)

        return {
            "status": "healthy",
            "notion_api": {
                "status": "connected",
                "api_version": settings.notion_api_version
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "notion_api": {
                "status": "disconnected",
                "error": str(e)
            }
        }
