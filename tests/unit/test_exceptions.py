"""Unit tests for exception hierarchy and error handling.

Tests cover:
- Exception initialization and attributes
- Exception serialization (to_dict)
- Exception hierarchy
- Correlation ID generation
- Error codes and status codes
"""

import pytest

from apigee_hybrid_mcp.exceptions import (
    AppError,
    AuthenticationError,
    AuthorizationError,
    ExpiredParameterError,
    ExternalServiceError,
    InvalidParameterError,
    MissingParameterError,
    ResourceAlreadyExistsError,
    ResourceNotFoundError,
    TimeoutError,
    ValidationError,
)


class TestAppError:
    """Test suite for base AppError class."""

    def test_app_error_initialization(self) -> None:
        """Test AppError initialization with all parameters."""
        error = AppError(
            message="Test error",
            code="TEST_ERROR",
            status=500,
            details={"key": "value"},
            correlation_id="test-id-123",
        )
        assert error.message == "Test error"
        assert error.code == "TEST_ERROR"
        assert error.status == 500
        assert error.details == {"key": "value"}
        assert error.correlation_id == "test-id-123"

    def test_app_error_defaults(self) -> None:
        """Test AppError with default values."""
        error = AppError(message="Test error")
        assert error.message == "Test error"
        assert error.code == "APP_ERROR"
        assert error.status == 500
        assert error.details == {}
        assert error.correlation_id is not None
        assert len(error.correlation_id) > 0

    def test_app_error_auto_correlation_id(self) -> None:
        """Test that correlation IDs are automatically generated."""
        error1 = AppError(message="Error 1")
        error2 = AppError(message="Error 2")
        assert error1.correlation_id != error2.correlation_id

    def test_app_error_to_dict(self) -> None:
        """Test serialization to dictionary."""
        error = AppError(
            message="Test error",
            code="TEST_ERROR",
            status=400,
            details={"param": "value"},
            correlation_id="test-123",
        )
        error_dict = error.to_dict()
        assert error_dict == {
            "error": {
                "code": "TEST_ERROR",
                "message": "Test error",
                "status": 400,
                "details": {"param": "value"},
                "correlation_id": "test-123",
            }
        }

    def test_app_error_str_representation(self) -> None:
        """Test string representation."""
        error = AppError(
            message="Test error",
            code="TEST_CODE",
            correlation_id="test-123",
        )
        error_str = str(error)
        assert "TEST_CODE" in error_str
        assert "Test error" in error_str
        assert "test-123" in error_str


class TestValidationError:
    """Test suite for ValidationError and subclasses."""

    def test_validation_error_status(self) -> None:
        """Test ValidationError has correct status code."""
        error = ValidationError(message="Validation failed")
        assert error.status == 422
        assert error.code == "VALIDATION_ERROR"

    def test_invalid_parameter_error(self) -> None:
        """Test InvalidParameterError initialization."""
        error = InvalidParameterError(
            parameter="email",
            value="invalid",
            reason="must be valid email format",
        )
        assert error.status == 422
        assert error.code == "INVALID_PARAMETER"
        assert "email" in error.message
        assert "must be valid email format" in error.message
        assert error.details["parameter"] == "email"
        assert error.details["reason"] == "must be valid email format"

    def test_missing_parameter_error(self) -> None:
        """Test MissingParameterError initialization."""
        error = MissingParameterError(parameter="organization")
        assert error.status == 422
        assert error.code == "MISSING_PARAMETER"
        assert "organization" in error.message
        assert error.details["parameter"] == "organization"

    def test_expired_parameter_error(self) -> None:
        """Test ExpiredParameterError initialization."""
        error = ExpiredParameterError(
            parameter="token",
            expired_at="2024-01-01T00:00:00Z",
        )
        assert error.status == 422
        assert error.code == "EXPIRED_PARAMETER"
        assert "token" in error.message
        assert error.details["parameter"] == "token"
        assert error.details["expired_at"] == "2024-01-01T00:00:00Z"

    def test_expired_parameter_error_without_timestamp(self) -> None:
        """Test ExpiredParameterError without expired_at timestamp."""
        error = ExpiredParameterError(parameter="session_id")
        assert error.status == 422
        assert "expired_at" not in error.details


class TestAuthenticationError:
    """Test suite for AuthenticationError."""

    def test_authentication_error_default(self) -> None:
        """Test AuthenticationError with default message."""
        error = AuthenticationError()
        assert error.status == 401
        assert error.code == "AUTHENTICATION_ERROR"
        assert error.message == "Authentication failed"

    def test_authentication_error_custom_message(self) -> None:
        """Test AuthenticationError with custom message."""
        error = AuthenticationError(
            message="Invalid credentials",
            details={"reason": "token_expired"},
        )
        assert error.status == 401
        assert error.message == "Invalid credentials"
        assert error.details["reason"] == "token_expired"


class TestAuthorizationError:
    """Test suite for AuthorizationError."""

    def test_authorization_error_default(self) -> None:
        """Test AuthorizationError with default message."""
        error = AuthorizationError()
        assert error.status == 403
        assert error.code == "AUTHORIZATION_ERROR"
        assert error.message == "Access denied"

    def test_authorization_error_with_resource(self) -> None:
        """Test AuthorizationError with resource information."""
        error = AuthorizationError(
            message="Cannot access resource",
            resource="teams/team-123",
        )
        assert error.status == 403
        assert error.details["resource"] == "teams/team-123"


class TestResourceErrors:
    """Test suite for resource-related errors."""

    def test_resource_not_found_error(self) -> None:
        """Test ResourceNotFoundError initialization."""
        error = ResourceNotFoundError(
            resource_type="team",
            resource_id="team-123",
        )
        assert error.status == 404
        assert error.code == "RESOURCE_NOT_FOUND"
        assert "team" in error.message.lower()
        assert "team-123" in error.message
        assert error.details["resource_type"] == "team"
        assert error.details["resource_id"] == "team-123"

    def test_resource_already_exists_error(self) -> None:
        """Test ResourceAlreadyExistsError initialization."""
        error = ResourceAlreadyExistsError(
            resource_type="team",
            resource_id="engineering-team",
        )
        assert error.status == 409
        assert error.code == "RESOURCE_ALREADY_EXISTS"
        assert "team" in error.message.lower()
        assert "engineering-team" in error.message
        assert error.details["resource_type"] == "team"
        assert error.details["resource_id"] == "engineering-team"


class TestTimeoutError:
    """Test suite for TimeoutError."""

    def test_timeout_error_default(self) -> None:
        """Test TimeoutError initialization."""
        error = TimeoutError(operation="API request")
        assert error.status == 408
        assert error.code == "TIMEOUT_ERROR"
        assert "API request" in error.message
        assert error.details["operation"] == "API request"

    def test_timeout_error_with_duration(self) -> None:
        """Test TimeoutError with timeout duration."""
        error = TimeoutError(
            operation="Database query",
            timeout_seconds=30,
        )
        assert error.status == 408
        assert error.details["timeout_seconds"] == 30


class TestExternalServiceError:
    """Test suite for ExternalServiceError."""

    def test_external_service_error_default(self) -> None:
        """Test ExternalServiceError with default parameters."""
        error = ExternalServiceError(service="apigee_api")
        assert error.status == 502
        assert error.code == "EXTERNAL_SERVICE_ERROR"
        assert "apigee_api" in error.message
        assert error.details["service"] == "apigee_api"

    def test_external_service_error_custom(self) -> None:
        """Test ExternalServiceError with custom parameters."""
        error = ExternalServiceError(
            service="google_cloud",
            message="Service temporarily unavailable",
            status=503,
            details={"retry_after": 60},
        )
        assert error.status == 503
        assert "google_cloud" in error.message
        assert "Service temporarily unavailable" in error.message
        assert error.details["retry_after"] == 60


class TestExceptionInheritance:
    """Test exception class hierarchy."""

    def test_validation_error_is_app_error(self) -> None:
        """Test ValidationError inherits from AppError."""
        error = ValidationError(message="Test")
        assert isinstance(error, AppError)
        assert isinstance(error, Exception)

    def test_invalid_parameter_is_validation_error(self) -> None:
        """Test InvalidParameterError inherits from ValidationError."""
        error = InvalidParameterError(
            parameter="test",
            value="",
            reason="test",
        )
        assert isinstance(error, ValidationError)
        assert isinstance(error, AppError)

    def test_all_errors_are_app_errors(self) -> None:
        """Test all custom exceptions inherit from AppError."""
        errors = [
            ValidationError(message="test"),
            InvalidParameterError(parameter="test", value="", reason="test"),
            MissingParameterError(parameter="test"),
            ExpiredParameterError(parameter="test"),
            AuthenticationError(),
            AuthorizationError(),
            ResourceNotFoundError(resource_type="test", resource_id="123"),
            ResourceAlreadyExistsError(resource_type="test", resource_id="123"),
            TimeoutError(operation="test"),
            ExternalServiceError(service="test"),
        ]

        for error in errors:
            assert isinstance(error, AppError)
            assert isinstance(error, Exception)
