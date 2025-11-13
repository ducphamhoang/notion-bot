"""Global error handler for standardizing error responses."""

import logging
from typing import Any, Dict

from fastapi import Request
from fastapi.responses import JSONResponse

from src.core.errors.exceptions import (
    DomainException,
    ValidationError,
    NotFoundError,
    ConflictError,
    NotionAPIError,
    RateLimitError,
    InternalError
)

logger = logging.getLogger(__name__)


def map_exception_to_error_code(exception: DomainException) -> tuple[str, int]:
    """Map domain exceptions to error codes and HTTP status codes."""
    
    if isinstance(exception, ValidationError):
        return "VALIDATION_ERROR", 400
    
    elif isinstance(exception, NotFoundError):
        return "NOT_FOUND", 404
    
    elif isinstance(exception, ConflictError):
        return "CONFLICT", 409
    
    elif isinstance(exception, RateLimitError):
        return "RATE_LIMIT_EXCEEDED", 503
    
    elif isinstance(exception, NotionAPIError):
        # Map Notion API errors to appropriate status codes
        if exception.status_code:
            if exception.status_code in [400, 403, 404]:
                return "NOTION_API_ERROR", exception.status_code
            elif exception.status_code == 429:
                return "RATE_LIMIT_EXCEEDED", 429
            else:
                return "NOTION_API_ERROR", 502
        return "NOTION_API_ERROR", 502
    
    elif isinstance(exception, InternalError):
        return "INTERNAL_ERROR", 500
    
    else:
        # Fallback for any other DomainException
        return "INTERNAL_ERROR", 500


def handle_domain_exception(exception: DomainException) -> JSONResponse:
    """Handle domain exceptions and return standardized error response."""
    
    error_code, status_code = map_exception_to_error_code(exception)
    
    # Log the error
    if status_code >= 500:
        logger.error(
            f"Server error: {exception.message}",
            exc_info=exception,
            extra={"error_details": exception.details}
        )
    else:
        logger.warning(
            f"Client error ({error_code}): {exception.message}",
            extra={"error_details": exception.details}
        )
    
    # Build error response
    error_response = {
        "error": {
            "code": error_code,
            "message": exception.message
        }
    }
    
    # Add details if available and appropriate
    if exception.details and error_code not in ["INTERNAL_ERROR"]:
        error_response["error"]["details"] = exception.details
    
    return JSONResponse(
        status_code=status_code,
        content=error_response
    )


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global exception handler for unhandled exceptions."""
    
    logger.error(
        f"Unhandled exception at {request.method} {request.url.path}: {str(exc)}",
        exc_info=exc
    )
    
    error_response = {
        "error": {
            "code": "INTERNAL_ERROR",
            "message": "An unexpected error occurred"
        }
    }
    
    return JSONResponse(
        status_code=500,
        content=error_response
    )
