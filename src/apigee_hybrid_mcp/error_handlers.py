"""Error handling and response formatting for MCP server.

This module provides centralized error handling, mapping exceptions to
appropriate HTTP status codes and JSON responses. It ensures consistent
error formatting across all endpoints.
"""

import traceback
from typing import Any, Dict, List

from mcp.types import TextContent

from apigee_hybrid_mcp.exceptions import AppError, ExternalServiceError
from apigee_hybrid_mcp.utils.logging import get_logger
from apigee_hybrid_mcp.validation import redact_sensitive_fields

logger = get_logger(__name__)


def format_error_response(
    error: Exception,
    operation: str,
    include_traceback: bool = False,
) -> List[TextContent]:
    """Format an exception into a structured MCP error response.

    This function handles both custom AppError exceptions and generic Python
    exceptions, providing consistent error formatting for clients.

    Args:
        error: The exception to format
        operation: Name of the operation that failed
        include_traceback: Whether to include stack trace (for unexpected errors)

    Returns:
        List of TextContent with formatted error information
    """
    if isinstance(error, AppError):
        # Use structured error information from AppError
        log_level = "warning" if error.status < 500 else "error"

        # Log with appropriate level
        log_data = {
            "operation": operation,
            "error_code": error.code,
            "error_message": error.message,
            "status": error.status,
            "correlation_id": error.correlation_id,
            "details": redact_sensitive_fields(error.details),
        }

        if log_level == "error":
            logger.error("app_error_occurred", **log_data)
        else:
            logger.warning("app_error_occurred", **log_data)

        # Format response
        response_text = f"""Error in {operation}

Error Code: {error.code}
Status: {error.status}
Message: {error.message}
Correlation ID: {error.correlation_id}

Details:
{_format_details(error.details)}"""

    else:
        # Handle unexpected generic exceptions
        error_message = str(error)
        error_type = type(error).__name__

        # Log unexpected error with stack trace
        logger.error(
            "unexpected_error",
            operation=operation,
            error_type=error_type,
            error_message=error_message,
            traceback=traceback.format_exc() if include_traceback else None,
        )

        # Format response
        response_text = f"""Unexpected Error in {operation}

Error Type: {error_type}
Message: {error_message}

This is an unexpected error. Please contact support with the details above."""

        if include_traceback:
            response_text += f"\n\nStack Trace:\n{traceback.format_exc()}"

    return [TextContent(type="text", text=response_text)]


def _format_details(details: Dict[str, Any], indent: int = 0) -> str:
    """Format error details dictionary as readable text.

    Args:
        details: Dictionary of error details
        indent: Indentation level for nested items

    Returns:
        Formatted string representation
    """
    if not details:
        return "  (none)"

    lines = []
    prefix = "  " * indent

    for key, value in details.items():
        if isinstance(value, dict):
            lines.append(f"{prefix}{key}:")
            lines.append(_format_details(value, indent + 1))
        elif isinstance(value, list):
            lines.append(f"{prefix}{key}: [{', '.join(str(v) for v in value)}]")
        else:
            lines.append(f"{prefix}{key}: {value}")

    return "\n".join(lines)


def handle_external_api_error(
    error: Exception,
    service: str,
    operation: str,
) -> List[TextContent]:
    """Handle errors from external APIs (Apigee, Google Cloud, etc.).

    This function wraps external API errors in ExternalServiceError for
    consistent handling and logging.

    Args:
        error: The exception from the external service
        service: Name of the external service
        operation: Operation that was being performed

    Returns:
        Formatted error response
    """
    # Check if it's already an AppError
    if isinstance(error, AppError):
        return format_error_response(error, operation)

    # Wrap in ExternalServiceError
    service_error = ExternalServiceError(
        service=service,
        message=str(error),
        details={"original_error": type(error).__name__},
    )

    return format_error_response(service_error, operation)


def create_validation_error_response(
    parameter: str,
    reason: str,
    operation: str,
) -> List[TextContent]:
    """Create a validation error response for quick parameter validation.

    Convenience function for creating validation errors without raising exceptions.

    Args:
        parameter: Name of the invalid parameter
        reason: Reason for validation failure
        operation: Operation being performed

    Returns:
        Formatted validation error response
    """
    from apigee_hybrid_mcp.exceptions import InvalidParameterError

    error = InvalidParameterError(parameter=parameter, value="", reason=reason)
    return format_error_response(error, operation)


class ErrorContext:
    """Context manager for structured error handling in tool handlers.

    Provides automatic error catching and formatting with operation context.

    Example:
        with ErrorContext("list-organizations"):
            # Tool implementation
            result = await client.get("organizations")
            return format_api_response(result, "List Organizations")
    """

    def __init__(self, operation: str, include_traceback: bool = True):
        """Initialize error context.

        Args:
            operation: Name of the operation for error messages
            include_traceback: Include stack trace for unexpected errors
        """
        self.operation = operation
        self.include_traceback = include_traceback
        self.result: Any = None

    def __enter__(self) -> "ErrorContext":
        """Enter context."""
        return self

    def __exit__(
        self,
        exc_type: Any,
        exc_val: Any,
        exc_tb: Any,
    ) -> bool:
        """Exit context and handle any exceptions.

        Returns:
            True to suppress the exception (it's been handled)
        """
        if exc_val is not None:
            self.result = format_error_response(
                exc_val,
                self.operation,
                self.include_traceback,
            )
            return True  # Suppress exception
        return False


def map_repository_error(error: Exception) -> AppError:
    """Map repository-specific errors to AppError hierarchy.

    Converts domain-specific repository exceptions into standard AppError
    exceptions for consistent error handling.

    Args:
        error: Repository exception

    Returns:
        Mapped AppError instance
    """
    from apigee_hybrid_mcp.exceptions import ResourceAlreadyExistsError, ResourceNotFoundError
    from apigee_hybrid_mcp.repository.team_repository import (
        TeamAlreadyExistsError,
        TeamNotFoundError,
    )

    if isinstance(error, TeamNotFoundError):
        return ResourceNotFoundError(
            resource_type="team",
            resource_id=error.team_id,
        )
    elif isinstance(error, TeamAlreadyExistsError):
        return ResourceAlreadyExistsError(
            resource_type="team",
            resource_id=error.team_name,
        )
    elif isinstance(error, AppError):
        return error
    else:
        # Wrap unknown errors
        return ExternalServiceError(
            service="repository",
            message=str(error),
            details={"error_type": type(error).__name__},
        )
