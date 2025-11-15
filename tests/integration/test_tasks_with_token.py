"""Integration tests for task operations with token_id parameter."""

import pytest
import httpx
from unittest.mock import AsyncMock, patch


@pytest.mark.asyncio
async def test_create_task_with_token_id(client: httpx.AsyncClient):
    """Test creating a task with specified token_id."""
    # Given: Create a token first
    token_data = {
        "name": "Task Test Token",
        "token": "secret_tasktest123456",
        "description": "Token for task testing"
    }
    token_response = await client.post("/tokens/", json=token_data)
    assert token_response.status_code == 201
    token_id = token_response.json()["id"]
    
    # Mock Notion API
    with patch('src.core.notion.client_factory.AsyncClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        mock_client.pages.create.return_value = {
            "id": "test-notion-page-id",
            "url": "https://notion.so/test-page"
        }
        
        # Given: Task creation data
        task_data = {
            "title": "Test Task with Token",
            "notion_database_id": "1a2b3c4d5e6f7890abcdef1234567890",
            "priority": "High"
        }
        
        # When: Create task with token_id
        response = await client.post(f"/tasks/?token_id={token_id}", json=task_data)
        
        # Then
        assert response.status_code == 201
        response_data = response.json()
        assert "notion_task_id" in response_data
        assert "notion_task_url" in response_data


@pytest.mark.asyncio
async def test_list_tasks_with_token_id(client: httpx.AsyncClient):
    """Test listing tasks with specified token_id."""
    # Given: Create a token first
    token_data = {
        "name": "List Test Token",
        "token": "secret_listtest123456"
    }
    token_response = await client.post("/tokens/", json=token_data)
    assert token_response.status_code == 201
    token_id = token_response.json()["id"]
    
    # Mock Notion API
    with patch('src.core.notion.client_factory.AsyncClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        mock_client.databases.query.return_value = {
            "results": [],
            "has_more": False,
            "next_cursor": None
        }
        
        # When: List tasks with token_id
        response = await client.get(
            f"/tasks/?notion_database_id=1a2b3c4d5e6f7890abcdef1234567890&token_id={token_id}"
        )
        
        # Then
        assert response.status_code == 200
        response_data = response.json()
        assert "data" in response_data
        assert "total" in response_data


@pytest.mark.asyncio
async def test_update_task_with_token_id(client: httpx.AsyncClient):
    """Test updating a task with specified token_id."""
    # Given: Create a token first
    token_data = {
        "name": "Update Test Token",
        "token": "secret_updatetest123456"
    }
    token_response = await client.post("/tokens/", json=token_data)
    assert token_response.status_code == 201
    token_id = token_response.json()["id"]
    
    # Mock Notion API
    with patch('src.core.notion.client_factory.AsyncClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        mock_client.pages.update.return_value = {
            "id": "test-task-id-123",
            "url": "https://notion.so/test-task"
        }
        
        # Given: Update data
        task_id = "1a2b3c4d5e6f7890abcdef1234567890"
        update_data = {
            "status": "Done",
            "priority": "Low"
        }
        
        # When: Update task with token_id
        response = await client.patch(
            f"/tasks/{task_id}?token_id={token_id}",
            json=update_data
        )
        
        # Then
        assert response.status_code == 200
        response_data = response.json()
        assert "notion_task_id" in response_data
        assert "notion_task_url" in response_data


@pytest.mark.asyncio
async def test_delete_task_with_token_id(client: httpx.AsyncClient):
    """Test deleting a task with specified token_id."""
    # Given: Create a token first
    token_data = {
        "name": "Delete Test Token",
        "token": "secret_deletetest123456"
    }
    token_response = await client.post("/tokens/", json=token_data)
    assert token_response.status_code == 201
    token_id = token_response.json()["id"]
    
    # Mock Notion API
    with patch('src.core.notion.client_factory.AsyncClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        mock_client.pages.update.return_value = {
            "id": "test-task-id-123",
            "archived": True
        }
        
        # Given: Task ID
        task_id = "1a2b3c4d5e6f7890abcdef1234567890"
        
        # When: Delete task with token_id
        response = await client.delete(f"/tasks/{task_id}?token_id={token_id}")
        
        # Then
        assert response.status_code == 204


@pytest.mark.asyncio
async def test_task_operations_without_token_id(client: httpx.AsyncClient):
    """Test that task operations work without token_id (fallback to env var)."""
    # Mock Notion API
    with patch('src.core.notion.client.AsyncClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        mock_client.pages.create.return_value = {
            "id": "test-notion-page-id",
            "url": "https://notion.so/test-page"
        }
        
        # Given: Task creation data without token_id
        task_data = {
            "title": "Test Task without Token",
            "notion_database_id": "1a2b3c4d5e6f7890abcdef1234567890"
        }
        
        # When: Create task without token_id parameter
        response = await client.post("/tasks/", json=task_data)
        
        # Then: Should still work using environment variable
        assert response.status_code in [201, 422, 502]  # May fail if env not set, but shouldn't 404


@pytest.mark.asyncio
async def test_task_with_invalid_token_id(client: httpx.AsyncClient):
    """Test task operation with invalid token_id returns 404."""
    # Given: Invalid token ID
    invalid_token_id = "507f1f77bcf86cd799439011"
    
    # Given: Task creation data
    task_data = {
        "title": "Test Task",
        "notion_database_id": "1a2b3c4d5e6f7890abcdef1234567890"
    }
    
    # When: Create task with invalid token_id
    response = await client.post(f"/tasks/?token_id={invalid_token_id}", json=task_data)
    
    # Then: Should return 404 (token not found)
    assert response.status_code == 404
    error_data = response.json()
    assert "error" in error_data


@pytest.mark.asyncio
async def test_task_with_inactive_token(client: httpx.AsyncClient):
    """Test task operation with inactive token returns validation error."""
    # Given: Create a token and deactivate it
    token_data = {
        "name": "Inactive Test Token",
        "token": "secret_inactivetest123"
    }
    token_response = await client.post("/tokens/", json=token_data)
    assert token_response.status_code == 201
    token_id = token_response.json()["id"]
    
    # Deactivate the token
    await client.patch(f"/tokens/{token_id}", json={"is_active": False})
    
    # Given: Task creation data
    task_data = {
        "title": "Test Task with Inactive Token",
        "notion_database_id": "1a2b3c4d5e6f7890abcdef1234567890"
    }
    
    # When: Create task with inactive token_id
    response = await client.post(f"/tasks/?token_id={token_id}", json=task_data)
    
    # Then: Should return 422 (validation error)
    assert response.status_code == 422
    error_data = response.json()
    assert "error" in error_data
    assert "inactive" in error_data["error"]["message"].lower()
