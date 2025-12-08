"""Resilience utilities including retry logic and circuit breakers."""

import functools
from typing import Any, Callable, Optional, Type, TypeVar

from circuitbreaker import CircuitBreaker
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from apigee_hybrid_mcp.utils.logging import get_logger

logger = get_logger(__name__)

T = TypeVar("T")


def create_circuit_breaker(
    failure_threshold: int = 5,
    timeout_duration: int = 60,
    name: Optional[str] = None,
) -> CircuitBreaker:
    """Create a circuit breaker instance.

    Args:
        failure_threshold: Number of failures before the circuit opens
        timeout_duration: Duration in seconds before attempting to close the circuit
        name: Optional name for the circuit breaker

    Returns:
        A configured CircuitBreaker instance
    """
    return CircuitBreaker(
        failure_threshold=failure_threshold,
        recovery_timeout=timeout_duration,
        name=name or "default",
    )


def with_retry(
    max_attempts: int = 3,
    backoff_factor: float = 2.0,
    exceptions: tuple[Type[Exception], ...] = (Exception,),
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorate a function to add retry logic.

    Args:
        max_attempts: Maximum number of retry attempts
        backoff_factor: Exponential backoff multiplier
        exceptions: Tuple of exception types to retry on

    Returns:
        Decorated function with retry logic
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @retry(
            stop=stop_after_attempt(max_attempts),
            wait=wait_exponential(multiplier=1, min=1, max=60),
            retry=retry_if_exception_type(exceptions),
            reraise=True,
        )
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            try:
                return await func(*args, **kwargs)
            except exceptions as e:
                logger.warning(
                    "retry_attempt",
                    function=func.__name__,
                    error=str(e),
                    attempt=wrapper.retry.statistics.get("attempt_number", 0),
                )
                raise

        return wrapper

    return decorator


class RateLimiter:
    """Simple token bucket rate limiter."""

    def __init__(self, requests_per_window: int, window_seconds: int):
        """Initialize rate limiter.

        Args:
            requests_per_window: Number of requests allowed per window
            window_seconds: Window duration in seconds
        """
        self.requests_per_window = requests_per_window
        self.window_seconds = window_seconds
        self.tokens = requests_per_window
        self.last_update = 0.0

    def acquire(self) -> bool:
        """Try to acquire a token.

        Returns:
            True if token acquired, False otherwise
        """
        import time

        now = time.time()
        time_passed = now - self.last_update

        # Refill tokens based on time passed
        self.tokens = min(
            self.requests_per_window,
            self.tokens + (time_passed * self.requests_per_window / self.window_seconds),
        )
        self.last_update = now

        if self.tokens >= 1:
            self.tokens -= 1
            return True
        return False
