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
                    # Notion client doesn't support timeout in async version,
                    # but we'll handle this in the rate limiter
                )
                
                # Test connection by listing databases
                try:
                    await _notion_client.databases.list()
                except Exception as e:
                    raise ValueError(
                        f"Failed to connect to Notion API. Please check your API key: {str(e)}"
                    )
    
    return _notion_client


async def test_notion_connection() -> dict:
    """Test Notion API connectivity."""
    try:
        client = await get_notion_client()
        result = await client.databases.list(limit=1)
        return {
            "status": "healthy",
            "notion_api": {
                "status": "connected",
                "api_version": "connected"
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
