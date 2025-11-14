"""Unit tests for user mapping service."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from src.features.users.dto.create_user_mapping_request import CreateUserMappingRequest
from src.features.users.services.user_mapping_service import UserMappingService
from src.features.users.models import UserMappingInDB
from src.core.errors.exceptions import NotFoundError


@pytest.fixture
def mock_repository():
    """Mock repository for testing."""
    return AsyncMock()


@pytest.fixture
def user_mapping_service(mock_repository):
    """Create user mapping service instance with mock repository."""
    return UserMappingService(repository=mock_repository)


@pytest.mark.asyncio
async def test_create_mapping_success(user_mapping_service, mock_repository):
    """Test successful creation of user mapping."""
    # Arrange
    request = CreateUserMappingRequest(
        platform="slack",
        platform_user_id="U123456",
        notion_user_id="12345678-1234-5678-9012-123456789012",
        display_name="Test User"
    )
    
    mock_mapping_in_db = UserMappingInDB(
        id="60f7b3b3b3b3b3b3b3b3b3b3",
        platform="slack",
        platform_user_id="U123456",
        notion_user_id="12345678-1234-5678-9012-123456789012",
        display_name="Test User"
    )
    
    mock_repository.create_mapping.return_value = mock_mapping_in_db
    
    # Act
    result = await user_mapping_service.create_mapping(request)
    
    # Assert
    assert result.platform == request.platform
    assert result.platform_user_id == request.platform_user_id
    assert result.notion_user_id == request.notion_user_id
    assert result.display_name == request.display_name
    mock_repository.create_mapping.assert_called_once()


@pytest.mark.asyncio
async def test_resolve_notion_user_id_success(user_mapping_service, mock_repository):
    """Test successful resolution of notion user ID."""
    # Arrange
    platform = "slack"
    platform_user_id = "U123456"
    expected_notion_user_id = "12345678-1234-5678-9012-123456789012"
    
    mock_mapping_in_db = UserMappingInDB(
        id="60f7b3b3b3b3b3b3b3b3b3b3",
        platform=platform,
        platform_user_id=platform_user_id,
        notion_user_id=expected_notion_user_id
    )
    
    mock_repository.find_by_platform_and_user_id.return_value = mock_mapping_in_db
    
    # Act
    result = await user_mapping_service.resolve_notion_user_id(platform, platform_user_id)
    
    # Assert
    assert result == expected_notion_user_id
    mock_repository.find_by_platform_and_user_id.assert_called_once_with(platform, platform_user_id)


@pytest.mark.asyncio
async def test_resolve_notion_user_id_not_found(user_mapping_service, mock_repository):
    """Test resolution failure when user mapping doesn't exist."""
    # Arrange
    platform = "slack"
    platform_user_id = "U123456"
    
    mock_repository.find_by_platform_and_user_id.return_value = None
    
    # Act & Assert
    with pytest.raises(NotFoundError) as exc_info:
        await user_mapping_service.resolve_notion_user_id(platform, platform_user_id)
    
    assert exc_info.value.entity_type == "UserMapping"
    assert exc_info.value.entity_id == f"{platform}:{platform_user_id}"


@pytest.mark.asyncio
async def test_get_mapping_by_platform_and_user_id_success(user_mapping_service, mock_repository):
    """Test successful retrieval of user mapping by platform and user ID."""
    # Arrange
    platform = "slack"
    platform_user_id = "U123456"
    
    mock_mapping_in_db = UserMappingInDB(
        id="60f7b3b3b3b3b3b3b3b3b3b3",
        platform=platform,
        platform_user_id=platform_user_id,
        notion_user_id="12345678-1234-5678-9012-123456789012"
    )
    
    mock_repository.find_by_platform_and_user_id.return_value = mock_mapping_in_db
    
    # Act
    result = await user_mapping_service.get_mapping_by_platform_and_user_id(platform, platform_user_id)
    
    # Assert
    assert result.platform == platform
    assert result.platform_user_id == platform_user_id
    mock_repository.find_by_platform_and_user_id.assert_called_once_with(platform, platform_user_id)


@pytest.mark.asyncio
async def test_get_mapping_by_platform_and_user_id_not_found(user_mapping_service, mock_repository):
    """Test retrieval failure when user mapping doesn't exist."""
    # Arrange
    platform = "slack"
    platform_user_id = "U123456"
    
    mock_repository.find_by_platform_and_user_id.return_value = None
    
    # Act & Assert
    with pytest.raises(NotFoundError) as exc_info:
        await user_mapping_service.get_mapping_by_platform_and_user_id(platform, platform_user_id)
    
    assert exc_info.value.entity_type == "UserMapping"
    assert exc_info.value.entity_id == f"{platform}:{platform_user_id}"


@pytest.mark.asyncio
async def test_get_mapping_by_id_success(user_mapping_service, mock_repository):
    """Test successful retrieval of user mapping by ID."""
    # Arrange
    mapping_id = "60f7b3b3b3b3b3b3b3b3b3b3"
    
    mock_mapping_in_db = UserMappingInDB(
        id=mapping_id,
        platform="slack",
        platform_user_id="U123456",
        notion_user_id="12345678-1234-5678-9012-123456789012"
    )
    
    mock_repository.find_by_id.return_value = mock_mapping_in_db
    
    # Act
    result = await user_mapping_service.get_mapping_by_id(mapping_id)
    
    # Assert
    assert result.id == mapping_id
    mock_repository.find_by_id.assert_called_once_with(mapping_id)


@pytest.mark.asyncio
async def test_get_mapping_by_id_not_found(user_mapping_service, mock_repository):
    """Test retrieval failure when user mapping doesn't exist by ID."""
    # Arrange
    mapping_id = "60f7b3b3b3b3b3b3b3b3b3b3"
    
    mock_repository.find_by_id.return_value = None
    
    # Act & Assert
    with pytest.raises(NotFoundError) as exc_info:
        await user_mapping_service.get_mapping_by_id(mapping_id)
    
    assert exc_info.value.entity_type == "UserMapping"
    assert exc_info.value.entity_id == mapping_id