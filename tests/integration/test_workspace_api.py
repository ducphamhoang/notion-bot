"""Integration tests for workspace management feature."""

import pytest
import httpx
from typing import AsyncGenerator

from src.main import app
from src.core.database.connection import DatabaseConnection


@pytest.fixture
async def client() -> AsyncGenerator[httpx.AsyncClient, None]:
    """Test HTTP client for API testing."""
    # Initialize test database connection
    await DatabaseConnection.get_database()

    async with httpx.AsyncClient(app=app, base_url="http://test") as client:
        yield client

    # Cleanup database connection
    await DatabaseConnection.close_connection()


@pytest.mark.asyncio
async def test_create_workspace(client: httpx.AsyncClient):
    """Test successful creation of workspace."""
    # Given
    request_data = {
        "platform": "slack",
        "platform_id": "C123456789",
        "notion_database_id": "1a2b3c4d5e6f7890abcdef1234567890",
        "name": "Test Workspace"
    }
    
    # When
    response = await client.post("/workspaces/", json=request_data)
    
    # Then
    assert response.status_code == 201
    response_data = response.json()
    assert response_data["platform"] == request_data["platform"]
    assert response_data["platform_id"] == request_data["platform_id"]
    assert response_data["notion_database_id"] == request_data["notion_database_id"]
    assert response_data["name"] == request_data["name"]
    assert "id" in response_data
    assert "created_at" in response_data
    assert "updated_at" in response_data


@pytest.mark.asyncio
async def test_get_workspace_by_platform(client: httpx.AsyncClient):
    """Test getting a workspace by platform and platform ID."""
    # Given: Create a workspace
    create_data = {
        "platform": "teams",
        "platform_id": "T987654321",
        "notion_database_id": "abcdef12345678901234567890abcdef", 
        "name": "Teams Workspace"
    }
    create_response = await client.post("/workspaces/", json=create_data)
    assert create_response.status_code == 201
    
    # When: Retrieve the workspace by platform and platform_id
    response = await client.get("/workspaces/query?platform=teams&platform_id=T987654321")
    
    # Then
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["platform"] == create_data["platform"]
    assert response_data["platform_id"] == create_data["platform_id"]
    assert response_data["notion_database_id"] == create_data["notion_database_id"]
    assert response_data["name"] == create_data["name"]


@pytest.mark.asyncio
async def test_get_workspace_by_platform_not_found(client: httpx.AsyncClient):
    """Test getting a non-existent workspace by platform and platform ID."""
    # When
    response = await client.get("/workspaces/query?platform=slack&platform_id=nonexistent")
    
    # Then
    assert response.status_code == 404
    error_data = response.json()
    assert "error" in error_data


@pytest.mark.asyncio
async def test_list_workspaces(client: httpx.AsyncClient):
    """Test listing workspaces."""
    # Given: Create multiple workspaces
    workspace1 = {
        "platform": "slack",
        "platform_id": "C111111",
        "notion_database_id": "1a2b3c4d5e6f7890abcdef1234567890",
        "name": "Workspace 1"
    }
    
    workspace2 = {
        "platform": "teams", 
        "platform_id": "T222222",
        "notion_database_id": "abcdef12345678901234567890abcdef",
        "name": "Workspace 2"
    }
    
    await client.post("/workspaces/", json=workspace1)
    await client.post("/workspaces/", json=workspace2)
    
    # When: List all workspaces
    response = await client.get("/workspaces/")
    
    # Then
    assert response.status_code == 200
    response_data = response.json()
    assert "workspaces" in response_data
    assert "count" in response_data
    assert response_data["count"] >= 2
    # Verify that our created workspaces are included
    platforms = [ws["platform"] for ws in response_data["workspaces"]]
    assert "slack" in platforms
    assert "teams" in platforms