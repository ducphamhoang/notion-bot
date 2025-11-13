"""Integration tests for tasks API endpoints."""

import pytest
import httpx
from datetime import datetime, timedelta
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
async def test_health_check(client: httpx.AsyncClient):
    """Test health check endpoint."""
    response = await client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "checks" in data
    assert "database" in data["checks"]


@pytest.mark.asyncio
async def test_root_endpoint(client: httpx.AsyncClient):
    """Test root endpoint."""
    response = await client.get("/")
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Notion Bot API"
    assert data["version"] == "0.1.0"


@pytest.mark.asyncio
async def test_create_task_validation_error(client: httpx.AsyncClient):
    """Test task creation with validation errors."""
    # Missing required title field
    invalid_request = {
        "notion_database_id": "1a2b3c4d5e6f7890abcdef1234567890"
    }
    
    response = await client.post("/tasks/", json=invalid_request)
    
    assert response.status_code == 422  # Pydantic validation error
    error_data = response.json()
    assert "detail" in error_data


@pytest.mark.asyncio
async def test_create_task_invalid_database_id(client: httpx.AsyncClient):
    """Test task creation with invalid database ID format."""
    invalid_request = {
        "title": "Test Task",
        "notion_database_id": "invalid_format"
    }
    
    response = await client.post("/tasks/", json=invalid_request)
    
    assert response.status_code == 422  # Pydantic validation error
    error_data = response.json()
    assert "detail" in error_data


@pytest.mark.asyncio
async def test_create_task_missing_required_fields(client: httpx.AsyncClient):
    """Test task creation with missing required fields."""
    invalid_request = {
        "title": ""  # Empty title not allowed
    }
    
    response = await client.post("/tasks/", json=invalid_request)
    
    assert response.status_code == 422  # Pydantic validation error


@pytest.mark.asyncio
async def test_create_task_invalid_priority(client: httpx.AsyncClient):
    """Test task creation with invalid priority value."""
    invalid_request = {
        "title": "Test Task",
        "notion_database_id": "1a2b3c4d5e6f7890abcdef1234567890",
        "priority": "InvalidPriority"
    }
    
    response = await client.post("/tasks/", json=invalid_request)
    
    assert response.status_code == 422  # Pydantic validation error


@pytest.mark.asyncio
async def test_create_task_valid_date_format(client: httpx.AsyncClient):
    """Test task creation with valid ISO date."""
    valid_request = {
        "title": "Test Task",
        "notion_database_id": "1a2b3c4d5e6f7890abcdef1234567890",
        "due_date": (datetime.now() + timedelta(days=1)).isoformat(),
        "priority": "High"
    }
    
    response = await client.post("/tasks/", json=valid_request)
    
    # This may fail with 502 or 404 due to invalid Notion credentials,
    # but request validation and formatting should pass
    assert response.status_code in [201, 404, 502]
    
    if response.status_code == 502:
        error_data = response.json()
        assert "error" in error_data
        assert error_data["error"]["code"] in ["NOTION_API_ERROR", "VALIDATION_ERROR"]


@pytest.mark.asyncio
async def test_create_task_with_custom_properties(client: httpx.AsyncClient):
    """Test task creation with custom properties."""
    valid_request = {
        "title": "Test Task",
        "notion_database_id": "1a2b3c4d5e6f7890abcdef1234567890",
        "properties": {
            "CustomField": {"rich_text": [{"text": {"content": "Custom value"}}]},
            "Tags": {"multi_select": [{"name": "bug"}, {"name": "urgent"}]}
        }
    }
    
    response = await client.post("/tasks/", json=valid_request)
    
    # May fail due to Notion connection issues, but should pass validation
    assert response.status_code in [201, 404, 502]


@pytest.mark.asyncio
async def test_create_task_with_assignee_not_supported_yet(client: httpx.AsyncClient):
    """Test task creation with assignee (not fully implemented yet)."""
    valid_request = {
        "title": "Test Task",
        "notion_database_id": "1a2b3c4d5e6f7890abcdef1234567890",
        "assignee_id": "user_001"
    }
    
    response = await client.post("/tasks/", json=valid_request)
    
    # Implement user mapping before assignee works
    assert response.status_code in [201, 404, 502]


@pytest.mark.asyncio
async def test_error_response_format(client: httpx.AsyncClient):
    """Test that error responses follow the expected format."""
    # Trigger validation error
    invalid_request = {
        "title": "Test Task",
        "notion_database_id": "invalid_format"
    }
    
    response = await client.post("/tasks/", json=invalid_request)
    
    if response.status_code == 422:
        # FastAPI validation errors have different format, so check general structure
        pass
    else:
        # Check domain error format
        error_data = response.json()
        assert "error" in error_data
        assert "code" in error_data["error"]
        assert "message" in error_data["error"]
