"""Exception hierarchy for Apigee Hybrid MCP Server.

This module defines a comprehensive exception hierarchy for the MCP server,
providing structured error handling with proper HTTP status codes, error codes,
and contextual information for debugging and client feedback.

Exception Hierarchy:
    AppError (base)
    ├── ValidationError
    │   ├── InvalidParameterError
    │   ├── MissingParameterError
    │   └── ExpiredParameterError
    ├── AuthenticationError
    ├── AuthorizationError
    ├── ResourceNotFoundError
    ├── ResourceAlreadyExistsError
    ├── TimeoutError
    └── ExternalServiceError

Each exception includes:
    - HTTP status code (for API responses)
    - Machine-readable error code
    - Human-readable message
    - Optional details dictionary
    - Correlation ID for tracking
"""

import uuid
from typing import Any, Dict, Optional


class AppError(Exception):
    """Base exception for all application errors.

    This is the root of the exception hierarchy. All custom exceptions
    should inherit from this class to ensure consistent error handling.

    Attributes:
        message: Human-readable error message
        code: Machine-readable error code (e.g., 'INVALID_PARAMETER')
        status: HTTP status code (e.g., 400, 401, 404, 500)
        details: Optional dictionary with additional context
        correlation_id: Unique identifier for error tracking
    """

    def __init__(
        self,
        message: str,
        code: str = "APP_ERROR",
        status: int = 500,
        details: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None,
    ):
        """Initialize the application error.

        Args:
            message: Human-readable error description
            code: Machine-readable error code
            status: HTTP status code
            details: Additional error context
            correlation_id: Unique error tracking ID (auto-generated if None)
        """
        super().__init__(message)
        self.message = message
        self.code = code
        self.status = status
        self.details = details or {}
        self.correlation_id = correlation_id or str(uuid.uuid4())

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for JSON serialization.

        Returns:
            Dictionary representation suitable for API responses
        """
        return {
            "error": {
                "code": self.code,
                "message": self.message,
                "status": self.status,
                "details": self.details,
                "correlation_id": self.correlation_id,
            }
        }

    def __str__(self) -> str:
        """String representation of the error."""
        return f"[{self.code}] {self.message} (correlation_id: {self.correlation_id})"


class ValidationError(AppError):
    """Base exception for validation-related errors.

    Raised when input validation fails. Status code is 422 (Unprocessable Entity).
    """

    def __init__(
        self,
        message: str,
        code: str = "VALIDATION_ERROR",
        details: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None,
    ):
        """Initialize validation error.

        Args:
            message: Human-readable validation error description
            code: Specific validation error code
            details: Additional validation context (e.g., field names)
            correlation_id: Unique error tracking ID
        """
        super().__init__(
            message=message,
            code=code,
            status=422,
            details=details,
            correlation_id=correlation_id,
        )


class InvalidParameterError(ValidationError):
    """Exception raised when a parameter value is invalid.

    Used for parameters that are present but don't meet validation criteria
    (e.g., wrong format, out of range, invalid type).
    """

    def __init__(
        self,
        parameter: str,
        value: Any,
        reason: str,
        details: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None,
    ):
        """Initialize invalid parameter error.

        Args:
            parameter: Name of the invalid parameter
            value: The invalid value (will be redacted if sensitive)
            reason: Why the value is invalid
            details: Additional context
            correlation_id: Unique error tracking ID
        """
        error_details = details or {}
        error_details.update({"parameter": parameter, "reason": reason})
        # Don't include value in details to avoid leaking sensitive data
        message = f"Invalid parameter '{parameter}': {reason}"
        super().__init__(
            message=message,
            code="INVALID_PARAMETER",
            details=error_details,
            correlation_id=correlation_id,
        )


class MissingParameterError(ValidationError):
    """Exception raised when a required parameter is missing.

    Used when a mandatory parameter is not provided in the request.
    """

    def __init__(
        self,
        parameter: str,
        details: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None,
    ):
        """Initialize missing parameter error.

        Args:
            parameter: Name of the missing parameter
            details: Additional context
            correlation_id: Unique error tracking ID
        """
        error_details = details or {}
        error_details.update({"parameter": parameter})
        message = f"Missing required parameter: '{parameter}'"
        super().__init__(
            message=message,
            code="MISSING_PARAMETER",
            details=error_details,
            correlation_id=correlation_id,
        )


class ExpiredParameterError(ValidationError):
    """Exception raised when a time-bound parameter has expired.

    Used for tokens, credentials, or session IDs that have exceeded
    their validity period.
    """

    def __init__(
        self,
        parameter: str,
        expired_at: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None,
    ):
        """Initialize expired parameter error.

        Args:
            parameter: Name of the expired parameter
            expired_at: ISO timestamp when parameter expired
            details: Additional context
            correlation_id: Unique error tracking ID
        """
        error_details = details or {}
        error_details.update({"parameter": parameter})
        if expired_at:
            error_details["expired_at"] = expired_at
        message = f"Parameter '{parameter}' has expired"
        super().__init__(
            message=message,
            code="EXPIRED_PARAMETER",
            details=error_details,
            correlation_id=correlation_id,
        )


class AuthenticationError(AppError):
    """Exception raised for authentication failures.

    Used when credentials are invalid, missing, or cannot be verified.
    Status code is 401 (Unauthorized).
    """

    def __init__(
        self,
        message: str = "Authentication failed",
        details: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None,
    ):
        """Initialize authentication error.

        Args:
            message: Human-readable authentication error description
            details: Additional context (avoid including credentials)
            correlation_id: Unique error tracking ID
        """
        super().__init__(
            message=message,
            code="AUTHENTICATION_ERROR",
            status=401,
            details=details,
            correlation_id=correlation_id,
        )


class AuthorizationError(AppError):
    """Exception raised for authorization failures.

    Used when a user is authenticated but lacks permission for the requested operation.
    Status code is 403 (Forbidden).
    """

    def __init__(
        self,
        message: str = "Access denied",
        resource: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None,
    ):
        """Initialize authorization error.

        Args:
            message: Human-readable authorization error description
            resource: Resource that was attempted to be accessed
            details: Additional context
            correlation_id: Unique error tracking ID
        """
        error_details = details or {}
        if resource:
            error_details["resource"] = resource
        super().__init__(
            message=message,
            code="AUTHORIZATION_ERROR",
            status=403,
            details=error_details,
            correlation_id=correlation_id,
        )


class ResourceNotFoundError(AppError):
    """Exception raised when a requested resource is not found.

    Status code is 404 (Not Found).
    """

    def __init__(
        self,
        resource_type: str,
        resource_id: str,
        details: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None,
    ):
        """Initialize resource not found error.

        Args:
            resource_type: Type of resource (e.g., 'team', 'proxy', 'environment')
            resource_id: Identifier of the missing resource
            details: Additional context
            correlation_id: Unique error tracking ID
        """
        error_details = details or {}
        error_details.update({"resource_type": resource_type, "resource_id": resource_id})
        message = f"{resource_type.capitalize()} not found: {resource_id}"
        super().__init__(
            message=message,
            code="RESOURCE_NOT_FOUND",
            status=404,
            details=error_details,
            correlation_id=correlation_id,
        )


class ResourceAlreadyExistsError(AppError):
    """Exception raised when attempting to create a resource that already exists.

    Status code is 409 (Conflict).
    """

    def __init__(
        self,
        resource_type: str,
        resource_id: str,
        details: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None,
    ):
        """Initialize resource already exists error.

        Args:
            resource_type: Type of resource (e.g., 'team', 'proxy')
            resource_id: Identifier of the conflicting resource
            details: Additional context
            correlation_id: Unique error tracking ID
        """
        error_details = details or {}
        error_details.update({"resource_type": resource_type, "resource_id": resource_id})
        message = f"{resource_type.capitalize()} already exists: {resource_id}"
        super().__init__(
            message=message,
            code="RESOURCE_ALREADY_EXISTS",
            status=409,
            details=error_details,
            correlation_id=correlation_id,
        )


class TimeoutError(AppError):
    """Exception raised when an operation times out.

    Status code is 408 (Request Timeout).
    """

    def __init__(
        self,
        operation: str,
        timeout_seconds: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None,
    ):
        """Initialize timeout error.

        Args:
            operation: Description of the operation that timed out
            timeout_seconds: Timeout duration in seconds
            details: Additional context
            correlation_id: Unique error tracking ID
        """
        error_details = details or {}
        error_details["operation"] = operation
        if timeout_seconds:
            error_details["timeout_seconds"] = timeout_seconds
        message = f"Operation timed out: {operation}"
        super().__init__(
            message=message,
            code="TIMEOUT_ERROR",
            status=408,
            details=error_details,
            correlation_id=correlation_id,
        )


class ExternalServiceError(AppError):
    """Exception raised when an external service fails.

    Used for failures in Apigee API, Google Cloud services, etc.
    Status code is 502 (Bad Gateway) or 503 (Service Unavailable).
    """

    def __init__(
        self,
        service: str,
        message: str = "External service error",
        status: int = 502,
        details: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None,
    ):
        """Initialize external service error.

        Args:
            service: Name of the external service
            message: Human-readable error description
            status: HTTP status code (502 or 503)
            details: Additional context
            correlation_id: Unique error tracking ID
        """
        error_details = details or {}
        error_details["service"] = service
        full_message = f"{service}: {message}"
        super().__init__(
            message=full_message,
            code="EXTERNAL_SERVICE_ERROR",
            status=status,
            details=error_details,
            correlation_id=correlation_id,
        )
