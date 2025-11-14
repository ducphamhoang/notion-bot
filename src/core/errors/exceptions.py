"""Custom exception classes for domain-specific errors."""


class DomainException(Exception):
    """Base exception for domain errors."""
    
    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class ValidationError(DomainException):
    """Raised when request validation fails."""
    
    def __init__(self, message: str, field: str | None = None, details: dict | None = None):
        if details is None:
            details = {}
        if field:
            details["field"] = field
        super().__init__(message, details)
        self.field = field


class NotFoundError(DomainException):
    """Raised when a requested entity is not found."""
    
    def __init__(self, entity_type: str, entity_id: str, details: dict | None = None):
        message = f"{entity_type} with ID '{entity_id}' not found"
        if details is None:
            details = {}
        details["entity_type"] = entity_type
        details["entity_id"] = entity_id
        super().__init__(message, details)
        self.entity_type = entity_type
        self.entity_id = entity_id


class ConflictError(DomainException):
    """Raised when a conflict occurs (e.g., duplicate resource)."""
    
    def __init__(self, message: str, conflict_details: dict | None = None):
        if conflict_details is None:
            conflict_details = {}
        super().__init__(message, conflict_details)


class NotionAPIError(DomainException):
    """Raised when Notion API calls fail."""

    def __init__(self, message: str, api_error: dict | str | None = None, status_code: int | None = None):
        if api_error is None:
            api_error = {}

        # Handle both dict and string error bodies
        if isinstance(api_error, dict):
            details = api_error.copy()
        elif isinstance(api_error, str):
            details = {"error": api_error}
        else:
            details = {}

        if status_code:
            details["status_code"] = status_code
        super().__init__(message, details)
        self.status_code = status_code


class RateLimitError(DomainException):
    """Raised when rate limits are exceeded."""
    
    def __init__(self, message: str, retry_after: int | None = None):
        details = {}
        if retry_after:
            details["retry_after"] = retry_after
        super().__init__(message, details)
        self.retry_after = retry_after


class InternalError(DomainException):
    """Raised for unexpected internal errors."""
    
    def __init__(self, message: str, original_error: Exception | None = None):
        details = {}
        if original_error:
            details["original_error"] = str(original_error)
            details["error_type"] = type(original_error).__name__
        super().__init__(message, details)
        self.original_error = original_error
