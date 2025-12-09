"""Request validation and parameter checking for MCP server.

This module provides comprehensive parameter validation including:
- Required parameter checking
- Type validation
- Format validation
- Range validation
- Pattern matching
- Expiration checking for time-bound credentials
- Sensitive field redaction
"""

import re
from datetime import datetime, timezone
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Set, TypeVar, cast

from pydantic import BaseModel, Field, field_validator

from apigee_hybrid_mcp.exceptions import (
    ExpiredParameterError,
    InvalidParameterError,
    MissingParameterError,
)
from apigee_hybrid_mcp.utils.logging import get_logger

logger = get_logger(__name__)

# Sensitive field patterns for redaction
SENSITIVE_FIELD_PATTERNS = [
    "token",
    "password",
    "secret",
    "key",
    "credential",
    "auth",
    "bearer",
    "api_key",
    "apikey",
]

F = TypeVar("F", bound=Callable[..., Any])


def redact_sensitive_fields(data: Dict[str, Any]) -> Dict[str, Any]:
    """Redact sensitive fields from a dictionary for logging.

    Args:
        data: Dictionary potentially containing sensitive data

    Returns:
        New dictionary with sensitive fields redacted
    """
    redacted: Dict[str, Any] = {}
    for key, value in data.items():
        key_lower = key.lower()
        is_sensitive = any(pattern in key_lower for pattern in SENSITIVE_FIELD_PATTERNS)

        if is_sensitive:
            redacted[key] = "***REDACTED***"
        elif isinstance(value, dict):
            redacted[key] = redact_sensitive_fields(value)
        elif isinstance(value, list):
            redacted_list: List[Any] = [
                redact_sensitive_fields(item) if isinstance(item, dict) else item for item in value
            ]
            redacted[key] = redacted_list
        else:
            redacted[key] = value

    return redacted


def validate_parameters(required: Optional[List[str]] = None) -> Callable[[F], F]:
    """Decorator to validate tool parameters before execution.

    Args:
        required: List of required parameter names

    Returns:
        Decorated function with parameter validation

    Example:
        @validate_parameters(required=["organization", "environment"])
        async def my_tool(arguments: Dict[str, Any]) -> Any:
            # arguments are validated here
            pass
    """
    required_params = required or []

    def decorator(func: F) -> F:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Extract arguments from function call
            arguments = kwargs.get("arguments", {})
            if not arguments and len(args) > 1:
                arguments = args[1] if isinstance(args[1], dict) else {}

            # Log validation attempt
            redacted_args = redact_sensitive_fields(arguments)
            logger.info(
                "validating_parameters",
                function=func.__name__,
                arguments=redacted_args,
                required=required_params,
            )

            # Check for missing required parameters
            for param in required_params:
                if param not in arguments or arguments[param] is None:
                    logger.warning(
                        "missing_required_parameter",
                        function=func.__name__,
                        parameter=param,
                    )
                    raise MissingParameterError(parameter=param)

            # Execute the function
            return await func(*args, **kwargs)

        return cast(F, wrapper)

    return decorator


class ParameterValidator:
    """Utility class for validating individual parameters.

    Provides static methods for common validation patterns.
    """

    @staticmethod
    def validate_non_empty_string(value: Any, parameter: str) -> str:
        """Validate that a parameter is a non-empty string.

        Args:
            value: Value to validate
            parameter: Parameter name for error messages

        Returns:
            Validated string value

        Raises:
            InvalidParameterError: If validation fails
        """
        if not isinstance(value, str):
            raise InvalidParameterError(
                parameter=parameter,
                value=type(value).__name__,
                reason="must be a string",
            )
        if not value.strip():
            raise InvalidParameterError(
                parameter=parameter,
                value="<empty>",
                reason="must not be empty",
            )
        return value

    @staticmethod
    def validate_positive_integer(value: Any, parameter: str) -> int:
        """Validate that a parameter is a positive integer.

        Args:
            value: Value to validate
            parameter: Parameter name for error messages

        Returns:
            Validated integer value

        Raises:
            InvalidParameterError: If validation fails
        """
        if not isinstance(value, int):
            raise InvalidParameterError(
                parameter=parameter,
                value=type(value).__name__,
                reason="must be an integer",
            )
        if value <= 0:
            raise InvalidParameterError(
                parameter=parameter,
                value=str(value),
                reason="must be positive",
            )
        return value

    @staticmethod
    def validate_email(value: Any, parameter: str) -> str:
        """Validate that a parameter is a valid email address.

        Args:
            value: Value to validate
            parameter: Parameter name for error messages

        Returns:
            Validated email string

        Raises:
            InvalidParameterError: If validation fails
        """
        if not isinstance(value, str):
            raise InvalidParameterError(
                parameter=parameter,
                value=type(value).__name__,
                reason="must be a string",
            )

        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_pattern, value):
            raise InvalidParameterError(
                parameter=parameter,
                value="<invalid_format>",
                reason="must be a valid email address",
            )
        return value

    @staticmethod
    def validate_pattern(value: Any, parameter: str, pattern: str, description: str) -> str:
        """Validate that a parameter matches a regex pattern.

        Args:
            value: Value to validate
            parameter: Parameter name for error messages
            pattern: Regular expression pattern
            description: Human-readable description of the pattern

        Returns:
            Validated string value

        Raises:
            InvalidParameterError: If validation fails
        """
        if not isinstance(value, str):
            raise InvalidParameterError(
                parameter=parameter,
                value=type(value).__name__,
                reason="must be a string",
            )

        if not re.match(pattern, value):
            raise InvalidParameterError(
                parameter=parameter,
                value="<invalid_format>",
                reason=f"must match pattern: {description}",
            )
        return value

    @staticmethod
    def validate_in_range(
        value: Any, parameter: str, min_val: Optional[int] = None, max_val: Optional[int] = None
    ) -> int:
        """Validate that an integer is within a specified range.

        Args:
            value: Value to validate
            parameter: Parameter name for error messages
            min_val: Minimum allowed value (inclusive)
            max_val: Maximum allowed value (inclusive)

        Returns:
            Validated integer value

        Raises:
            InvalidParameterError: If validation fails
        """
        if not isinstance(value, int):
            raise InvalidParameterError(
                parameter=parameter,
                value=type(value).__name__,
                reason="must be an integer",
            )

        if min_val is not None and value < min_val:
            raise InvalidParameterError(
                parameter=parameter,
                value=str(value),
                reason=f"must be at least {min_val}",
            )

        if max_val is not None and value > max_val:
            raise InvalidParameterError(
                parameter=parameter,
                value=str(value),
                reason=f"must be at most {max_val}",
            )

        return value

    @staticmethod
    def validate_enum(value: Any, parameter: str, allowed_values: List[str]) -> str:
        """Validate that a parameter is one of allowed values.

        Args:
            value: Value to validate
            parameter: Parameter name for error messages
            allowed_values: List of allowed values

        Returns:
            Validated value

        Raises:
            InvalidParameterError: If validation fails
        """
        if not isinstance(value, str):
            raise InvalidParameterError(
                parameter=parameter,
                value=type(value).__name__,
                reason="must be a string",
            )

        if value not in allowed_values:
            raise InvalidParameterError(
                parameter=parameter,
                value=value,
                reason=f"must be one of: {', '.join(allowed_values)}",
            )
        return value

    @staticmethod
    def validate_not_expired(
        timestamp: str,
        parameter: str,
        current_time: Optional[datetime] = None,
    ) -> None:
        """Validate that a timestamp has not expired.

        Args:
            timestamp: ISO 8601 timestamp string
            parameter: Parameter name for error messages
            current_time: Current time for comparison (defaults to now)

        Raises:
            ExpiredParameterError: If timestamp has expired
            InvalidParameterError: If timestamp format is invalid
        """
        try:
            expiry_time = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        except (ValueError, AttributeError) as e:
            raise InvalidParameterError(
                parameter=parameter,
                value="<invalid_timestamp>",
                reason=f"must be valid ISO 8601 timestamp: {str(e)}",
            )

        check_time = current_time or datetime.now(timezone.utc)

        if expiry_time < check_time:
            raise ExpiredParameterError(
                parameter=parameter,
                expired_at=timestamp,
            )

    @staticmethod
    def validate_list_not_empty(value: Any, parameter: str) -> List[Any]:
        """Validate that a parameter is a non-empty list.

        Args:
            value: Value to validate
            parameter: Parameter name for error messages

        Returns:
            Validated list

        Raises:
            InvalidParameterError: If validation fails
        """
        if not isinstance(value, list):
            raise InvalidParameterError(
                parameter=parameter,
                value=type(value).__name__,
                reason="must be a list",
            )

        if len(value) == 0:
            raise InvalidParameterError(
                parameter=parameter,
                value="<empty_list>",
                reason="must not be empty",
            )

        return value

    @staticmethod
    def validate_unique_items(value: List[Any], parameter: str) -> List[Any]:
        """Validate that all items in a list are unique.

        Args:
            value: List to validate
            parameter: Parameter name for error messages

        Returns:
            Validated list

        Raises:
            InvalidParameterError: If list contains duplicates
        """
        if not isinstance(value, list):
            raise InvalidParameterError(
                parameter=parameter,
                value=type(value).__name__,
                reason="must be a list",
            )

        seen: Set[Any] = set()
        duplicates: Set[Any] = set()

        for item in value:
            # Handle unhashable types
            try:
                if item in seen:
                    duplicates.add(item)
                seen.add(item)
            except TypeError:
                # For unhashable types, just continue
                pass

        if duplicates:
            raise InvalidParameterError(
                parameter=parameter,
                value="<contains_duplicates>",
                reason=f"must contain unique items, found duplicates: {duplicates}",
            )

        return value


class ToolParametersBase(BaseModel):
    """Base class for tool parameter validation schemas.

    All tool-specific parameter schemas should inherit from this class
    to ensure consistent validation behavior.
    """

    model_config = {
        "extra": "forbid",  # Reject unknown fields
        "str_strip_whitespace": True,  # Strip whitespace from strings
        "validate_assignment": True,  # Validate on attribute assignment
    }


class OrganizationParameters(ToolParametersBase):
    """Parameters for tools requiring organization ID."""

    organization: str = Field(
        ...,
        min_length=1,
        description="Apigee organization ID",
    )


class EnvironmentParameters(OrganizationParameters):
    """Parameters for tools requiring organization and environment."""

    environment: str = Field(
        ...,
        min_length=1,
        description="Environment name",
    )


class ProxyParameters(EnvironmentParameters):
    """Parameters for tools working with API proxies."""

    proxy: str = Field(
        ...,
        min_length=1,
        description="API proxy name",
    )
    revision: Optional[str] = Field(
        None,
        description="Proxy revision number",
    )


class DebugSessionParameters(ProxyParameters):
    """Parameters for debug session creation."""

    session: str = Field(
        ...,
        min_length=1,
        description="Debug session ID",
    )
    timeout: Optional[int] = Field(
        None,
        ge=1,
        le=600,
        description="Session timeout in seconds (1-600)",
    )

    @field_validator("timeout")
    @classmethod
    def validate_timeout(cls, v: Optional[int]) -> Optional[int]:
        """Validate timeout is within acceptable range."""
        if v is not None and (v < 1 or v > 600):
            raise ValueError("timeout must be between 1 and 600 seconds")
        return v
