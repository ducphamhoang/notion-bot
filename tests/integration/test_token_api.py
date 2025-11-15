"""Integration tests for token management API."""

import pytest
import httpx


@pytest.mark.asyncio
async def test_create_token(client: httpx.AsyncClient):
    """Test successful creation of token."""
    # Given
    request_data = {
        "name": "Test Token",
        "token": "secret_test123456789abc",
        "description": "Test token description"
    }
    
    # When
    response = await client.post("/tokens/", json=request_data)
    
    # Then
    assert response.status_code == 201
    response_data = response.json()
    assert response_data["name"] == request_data["name"]
    assert response_data["token_preview"] == "******...9abc"  # Last 6 chars masked
    assert response_data["description"] == request_data["description"]
    assert response_data["is_active"] is True
    assert "id" in response_data
    assert "created_at" in response_data
    assert "updated_at" in response_data
    # Ensure raw token is never in response
    assert "secret_" not in str(response_data)


@pytest.mark.asyncio
async def test_create_token_invalid_format(client: httpx.AsyncClient):
    """Test token creation with invalid token format."""
    # Given
    request_data = {
        "name": "Invalid Token",
        "token": "invalid_token_format",  # Doesn't start with 'secret_'
        "description": "This should fail"
    }
    
    # When
    response = await client.post("/tokens/", json=request_data)
    
    # Then
    assert response.status_code == 422
    error_data = response.json()
    assert "error" in error_data


@pytest.mark.asyncio
async def test_list_tokens(client: httpx.AsyncClient):
    """Test listing all tokens."""
    # Given: Create multiple tokens
    token1 = {
        "name": "Token 1",
        "token": "secret_token1abc123",
        "description": "First token"
    }
    token2 = {
        "name": "Token 2",
        "token": "secret_token2xyz789"
    }
    
    await client.post("/tokens/", json=token1)
    await client.post("/tokens/", json=token2)
    
    # When
    response = await client.get("/tokens/")
    
    # Then
    assert response.status_code == 200
    response_data = response.json()
    assert "tokens" in response_data
    assert "total" in response_data
    assert response_data["total"] >= 2
    
    # Verify all tokens are masked
    for token in response_data["tokens"]:
        assert "token_preview" in token
        assert token["token_preview"].startswith("******...")
        assert "secret_" not in str(token)


@pytest.mark.asyncio
async def test_get_token_by_id(client: httpx.AsyncClient):
    """Test getting a single token by ID."""
    # Given: Create a token
    create_data = {
        "name": "Get Test Token",
        "token": "secret_gettest123456",
        "description": "Token for get test"
    }
    create_response = await client.post("/tokens/", json=create_data)
    assert create_response.status_code == 201
    token_id = create_response.json()["id"]
    
    # When
    response = await client.get(f"/tokens/{token_id}")
    
    # Then
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["id"] == token_id
    assert response_data["name"] == create_data["name"]
    assert response_data["description"] == create_data["description"]
    assert response_data["token_preview"] == "******...t123456"


@pytest.mark.asyncio
async def test_get_token_not_found(client: httpx.AsyncClient):
    """Test getting a non-existent token."""
    # Given: Invalid token ID
    invalid_id = "507f1f77bcf86cd799439011"
    
    # When
    response = await client.get(f"/tokens/{invalid_id}")
    
    # Then
    assert response.status_code == 404
    error_data = response.json()
    assert "error" in error_data


@pytest.mark.asyncio
async def test_update_token(client: httpx.AsyncClient):
    """Test updating a token."""
    # Given: Create a token
    create_data = {
        "name": "Original Name",
        "token": "secret_original123456",
        "description": "Original description"
    }
    create_response = await client.post("/tokens/", json=create_data)
    assert create_response.status_code == 201
    token_id = create_response.json()["id"]
    
    # When: Update the token
    update_data = {
        "name": "Updated Name",
        "description": "Updated description",
        "is_active": False
    }
    response = await client.patch(f"/tokens/{token_id}", json=update_data)
    
    # Then
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["name"] == update_data["name"]
    assert response_data["description"] == update_data["description"]
    assert response_data["is_active"] is False


@pytest.mark.asyncio
async def test_delete_token(client: httpx.AsyncClient):
    """Test deleting a token."""
    # Given: Create a token
    create_data = {
        "name": "Token to Delete",
        "token": "secret_delete123456"
    }
    create_response = await client.post("/tokens/", json=create_data)
    assert create_response.status_code == 201
    token_id = create_response.json()["id"]
    
    # When: Delete the token
    response = await client.delete(f"/tokens/{token_id}")
    
    # Then
    assert response.status_code == 204
    
    # Verify token is deleted
    get_response = await client.get(f"/tokens/{token_id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_token_not_found(client: httpx.AsyncClient):
    """Test deleting a non-existent token."""
    # Given: Invalid token ID
    invalid_id = "507f1f77bcf86cd799439011"
    
    # When
    response = await client.delete(f"/tokens/{invalid_id}")
    
    # Then
    assert response.status_code == 404
    error_data = response.json()
    assert "error" in error_data


@pytest.mark.asyncio
async def test_list_tokens_active_only_filter(client: httpx.AsyncClient):
    """Test listing tokens with active_only filter."""
    # Given: Create one active and one inactive token
    active_token = {
        "name": "Active Token",
        "token": "secret_active123456"
    }
    inactive_token = {
        "name": "Inactive Token",
        "token": "secret_inactive123"
    }
    
    active_response = await client.post("/tokens/", json=active_token)
    inactive_response = await client.post("/tokens/", json=inactive_token)
    inactive_id = inactive_response.json()["id"]
    
    # Deactivate the second token
    await client.patch(f"/tokens/{inactive_id}", json={"is_active": False})
    
    # When: List only active tokens
    response = await client.get("/tokens/?active_only=true")
    
    # Then
    assert response.status_code == 200
    response_data = response.json()
    
    # All returned tokens should be active
    for token in response_data["tokens"]:
        assert token["is_active"] is True
