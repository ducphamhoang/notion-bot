"""Unit tests for token service."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime
from bson import ObjectId

from src.features.tokens.services.token_service import TokenService
from src.features.tokens.dto.create_token_request import CreateTokenRequest
from src.features.tokens.dto.update_token_request import UpdateTokenRequest
from src.features.tokens.models import NotionToken
from src.core.errors.exceptions import NotFoundError, ValidationError


@pytest.fixture
def mock_repository():
    """Mock repository for testing."""
    return AsyncMock()


@pytest.fixture
def token_service(mock_repository):
    """Create token service instance with mock repository."""
    return TokenService(repository=mock_repository)


@pytest.mark.asyncio
async def test_create_token_success(token_service, mock_repository):
    """Test successful creation of token."""
    # Arrange
    request = CreateTokenRequest(
        name="Test Token",
        token="secret_abc123xyz789",
        description="Test token description"
    )
    
    created_token = NotionToken(
        _id=ObjectId(),
        name=request.name,
        token=request.token,
        description=request.description,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        is_active=True
    )
    
    mock_repository.create.return_value = created_token
    
    # Act
    result = await token_service.create_token(request)
    
    # Assert
    assert result.name == request.name
    assert result.token_preview == "******...x789"  # Last 6 chars
    assert result.description == request.description
    assert result.is_active is True
    mock_repository.create.assert_called_once()


@pytest.mark.asyncio
async def test_list_tokens_masks_values(token_service, mock_repository):
    """Test that list_tokens masks all token values."""
    # Arrange
    tokens = [
        NotionToken(
            _id=ObjectId(),
            name="Token 1",
            token="secret_token1abc123",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            is_active=True
        ),
        NotionToken(
            _id=ObjectId(),
            name="Token 2",
            token="secret_token2xyz789",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            is_active=True
        ),
    ]
    
    mock_repository.list_all.return_value = tokens
    
    # Act
    result = await token_service.list_tokens()
    
    # Assert
    assert result.total == 2
    assert len(result.tokens) == 2
    assert result.tokens[0].token_preview == "******...c123"
    assert result.tokens[1].token_preview == "******...z789"
    mock_repository.list_all.assert_called_once_with(active_only=True)


@pytest.mark.asyncio
async def test_get_token_not_found(token_service, mock_repository):
    """Test get_token raises NotFoundError when token doesn't exist."""
    # Arrange
    token_id = str(ObjectId())
    mock_repository.get_by_id.side_effect = NotFoundError(
        entity_type="Token",
        entity_id=token_id
    )
    
    # Act & Assert
    with pytest.raises(NotFoundError) as exc_info:
        await token_service.get_token(token_id)
    
    assert exc_info.value.entity_type == "Token"
    assert exc_info.value.entity_id == token_id


@pytest.mark.asyncio
async def test_update_token_success(token_service, mock_repository):
    """Test successful token update."""
    # Arrange
    token_id = str(ObjectId())
    request = UpdateTokenRequest(
        name="Updated Token",
        description="Updated description"
    )
    
    updated_token = NotionToken(
        _id=ObjectId(token_id),
        name=request.name,
        token="secret_originaltoken123",
        description=request.description,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        is_active=True
    )
    
    mock_repository.update.return_value = updated_token
    
    # Act
    result = await token_service.update_token(token_id, request)
    
    # Assert
    assert result.name == request.name
    assert result.description == request.description
    mock_repository.update.assert_called_once()
    # Verify updates dict contains expected fields
    call_args = mock_repository.update.call_args
    assert call_args[0][0] == token_id
    assert "name" in call_args[0][1]
    assert "description" in call_args[0][1]


@pytest.mark.asyncio
async def test_update_token_no_fields(token_service, mock_repository):
    """Test update_token raises ValidationError when no fields provided."""
    # Arrange
    token_id = str(ObjectId())
    request = UpdateTokenRequest()
    
    # Act & Assert
    with pytest.raises(ValidationError) as exc_info:
        await token_service.update_token(token_id, request)
    
    assert "No fields to update" in exc_info.value.message


@pytest.mark.asyncio
async def test_delete_token_success(token_service, mock_repository):
    """Test successful token deletion."""
    # Arrange
    token_id = str(ObjectId())
    mock_repository.delete.return_value = True
    
    # Act
    await token_service.delete_token(token_id)
    
    # Assert
    mock_repository.delete.assert_called_once_with(token_id)


@pytest.mark.asyncio
async def test_delete_token_not_found(token_service, mock_repository):
    """Test delete_token raises NotFoundError when token doesn't exist."""
    # Arrange
    token_id = str(ObjectId())
    mock_repository.delete.side_effect = NotFoundError(
        entity_type="Token",
        entity_id=token_id
    )
    
    # Act & Assert
    with pytest.raises(NotFoundError) as exc_info:
        await token_service.delete_token(token_id)
    
    assert exc_info.value.entity_type == "Token"


def test_mask_token_function():
    """Test static mask_token method with various inputs."""
    # Test normal token
    assert TokenService.mask_token("secret_abc123xyz789") == "******...z789"
    
    # Test short token (6 chars or less)
    assert TokenService.mask_token("short") == "******"
    
    # Test exactly 6 chars
    assert TokenService.mask_token("abcdef") == "******"
    
    # Test 7 chars (shows last 6)
    assert TokenService.mask_token("abcdefg") == "******...bcdefg"
