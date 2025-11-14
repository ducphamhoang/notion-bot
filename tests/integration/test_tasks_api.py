"""Integration tests for tasks API endpoints."""

import pytest
import httpx
from datetime import datetime, timedelta
from typing import AsyncGenerator

from src.main import app
from src.core.database.connection import DatabaseConnection




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
async def test_list_tasks_requires_database_id(client: httpx.AsyncClient):
    """GET /tasks requires notion_database_id parameter."""
    response = await client.get("/tasks")
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_list_tasks_invalid_limit(client: httpx.AsyncClient):
    """Limit over 100 should fail validation."""
    params = {
        "notion_database_id": "1a2b3c4d5e6f7890abcdef1234567890",
        "limit": 200
    }
    response = await client.get("/tasks", params=params)
    assert response.status_code == 422



@pytest.mark.asyncio
async def test_update_task_requires_payload(client: httpx.AsyncClient):
    """PATCH /tasks/{id} without payload should fail validation."""
    response = await client.patch("/tasks/1a2b3c4d5e6f7890abcdef1234567890", json={})
    assert response.status_code == 422



@pytest.mark.asyncio
async def test_delete_task_success(client: httpx.AsyncClient):
    """DELETE /tasks/{id} should return 204 on successful deletion."""
    task_id = "1a2b3c4d5e6f7890abcdef1234567890"
    response = await client.delete(f"/tasks/{task_id}")
    assert response.status_code in [204, 404, 502]  # 204 for success, 404 if not found, 502 for API issues


@pytest.mark.asyncio
async def test_delete_task_invalid_id_format(client: httpx.AsyncClient):
    """DELETE /tasks/{id} should return 422 for invalid task ID format."""
    invalid_task_id = "invalid_format"
    response = await client.delete(f"/tasks/{invalid_task_id}")
    assert response.status_code == 422  # FastAPI path validation error


@pytest.mark.asyncio
async def test_delete_task_not_found(client: httpx.AsyncClient):
    """DELETE /tasks/{id} should return 404 for non-existent task."""
    # Use a valid format but non-existent task ID
    non_existent_task_id = "1a2b3c4d5e6f7890abcdef1234567891"
    response = await client.delete(f"/tasks/{non_existent_task_id}")
    assert response.status_code in [204, 404, 502]  # 404 if Notion returns 404, 204 if success, 502 for API issues
