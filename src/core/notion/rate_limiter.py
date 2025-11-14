"""Rate limit handling for Notion API with exponential backoff and jitter."""

import asyncio
import random
import logging
from functools import wraps
from typing import Any, Callable, Coroutine, TypeVar

from notion_client import APIResponseError

from src.core.errors.exceptions import RateLimitError
from src.core.monitoring.metrics import get_metrics_collector

logger = logging.getLogger(__name__)

T = TypeVar("T")


def with_retry(
    max_retries: int = 4,
    initial_delay: float = 1.0,
    max_delay: float = 8.0,
    jitter_factor: float = 0.2,
) -> Callable[[Callable[..., Coroutine[Any, Any, T]]], Callable[..., Coroutine[Any, Any, T]]]:
    """
    Decorator to add retry logic with exponential backoff and jitter.
    
    Args:
        max_retries: Maximum number of retries after rate limit hits
        initial_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        jitter_factor: Jitter factor (0.0 = no jitter, 1.0 = full jitter)
    
    Returns:
        Decorated coroutine function
    """
    def decorator(func: Callable[..., Coroutine[Any, Any, T]]) -> Callable[..., Coroutine[Any, Any, T]]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            last_error = None
            metrics = get_metrics_collector()
            
            for attempt in range(max_retries + 1):
                try:
                    # Track Notion API call
                    await metrics.increment_notion_api_calls()
                    return await func(*args, **kwargs)
                except APIResponseError as e:
                    last_error = e
                    
                    # Check if it's a rate limit error (429)
                    if e.status == 429 or "rate_limit" in str(e.body).lower():
                        # Track rate limit hit
                        await metrics.increment_rate_limit_hits()
                        
                        if attempt < max_retries:
                            # Calculate exponential backoff with jitter
                            delay = min(
                                initial_delay * (2 ** attempt),
                                max_delay
                            )
                            
                            # Add random jitter (±jitter_factor)
                            if jitter_factor > 0:
                                jitter = delay * jitter_factor * random.uniform(-1, 1)
                                delay = max(0, delay + jitter)
                            
                            logger.warning(
                                f"Rate limit hit, retrying in {delay:.2f}s "
                                f"(attempt {attempt + 1}/{max_retries + 1})"
                            )
                            
                            await asyncio.sleep(delay)
                            continue
                        else:
                            # Max retries exceeded
                            logger.error(
                                f"Rate limit exceeded after {max_retries + 1} attempts"
                            )
                            raise RateLimitError(
                                "Notion API rate limit exceeded. Please try again later."
                            )
                    else:
                        # Not a rate limit error, re-raise immediately
                        raise
                
                # Handle other exceptions (should be rare)
                except Exception as e:
                    last_error = e
                    raise
            
            # This should never be reached, but just in case
            if last_error:
                raise last_error
            
            raise RuntimeError("Unexpected error in retry decorator")
        
        return wrapper
    return decorator
