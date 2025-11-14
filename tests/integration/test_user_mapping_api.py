"""Integration tests for user mapping feature."""

import pytest
import httpx
from typing import AsyncGenerator
from motor.motor_asyncio import AsyncIOMotorClient

from src.main import app
from src.config.settings import get_settings
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
async def test_create_user_mapping(client: httpx.AsyncClient):
    """Test successful creation of user mapping."""
    # Given
    request_data = {
        "platform": "slack",
        "platform_user_id": "U123456789",
        "notion_user_id": "12345678-1234-5678-9012-123456789012",
        "display_name": "Test User"
    }
    
    # When
    response = await client.post("/users/mappings/", json=request_data)
    
    # Then
    assert response.status_code == 201
    response_data = response.json()
    assert response_data["platform"] == request_data["platform"]
    assert response_data["platform_user_id"] == request_data["platform_user_id"]
    assert response_data["notion_user_id"] == request_data["notion_user_id"]
    assert response_data["display_name"] == request_data["display_name"]
    assert "id" in response_data
    assert "created_at" in response_data
    assert "updated_at" in response_data


@pytest.mark.asyncio
async def test_get_user_mapping_by_id(client: httpx.AsyncClient):
    """Test getting a user mapping by ID."""
    # Given: Create a user mapping
    create_data = {
        "platform": "teams",
        "platform_user_id": "T987654321",
        "notion_user_id": "98765432-9876-5432-1098-987654321098",
        "display_name": "Team User"
    }
    create_response = await client.post("/users/mappings/", json=create_data)
    assert create_response.status_code == 201
    created_id = create_response.json()["id"]
    
    # When: Retrieve the mapping by ID
    response = await client.get(f"/users/mappings/{created_id}")
    
    # Then
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["id"] == created_id
    assert response_data["platform"] == create_data["platform"]
    assert response_data["platform_user_id"] == create_data["platform_user_id"]
    assert response_data["display_name"] == create_data["display_name"]


@pytest.mark.asyncio
async def test_get_user_mapping_by_id_not_found(client: httpx.AsyncClient):
    """Test getting a non-existent user mapping by ID."""
    # When
    response = await client.get("/users/mappings/nonexistent_id")
    
    # Then
    assert response.status_code == 404
    error_data = response.json()
    assert "error" in error_data


@pytest.mark.asyncio
async def test_resolve_user_mapping(client: httpx.AsyncClient):
    """Test resolving a user mapping by platform and platform user ID."""
    # Given: Create a user mapping
    create_data = {
        "platform": "slack",
        "platform_user_id": "U999999",
        "notion_user_id": "11111111-2222-3333-4444-555555555555",
        "display_name": "Resolved User"
    }
    create_response = await client.post("/users/mappings/", json=create_data)
    assert create_response.status_code == 201
    
    # When: Resolve the mapping
    response = await client.get("/users/mappings/resolve?platform=slack&platform_user_id=U999999")
    
    # Then
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["platform"] == create_data["platform"]
    assert response_data["platform_user_id"] == create_data["platform_user_id"]
    assert response_data["notion_user_id"] == create_data["notion_user_id"]
    assert response_data["display_name"] == create_data["display_name"]


@pytest.mark.asyncio
async def test_resolve_user_mapping_not_found(client: httpx.AsyncClient):
    """Test resolving a non-existent user mapping."""
    # When
    response = await client.get("/users/mappings/resolve?platform=slack&platform_user_id=nonexistent")
    
    # Then
    assert response.status_code == 404
    error_data = response.json()
    assert "error" in error_data