"""Unit tests for error handlers and response formatting.

Tests cover:
- Error response formatting
- Error context manager
- Repository error mapping
- External API error handling
"""

from apigee_hybrid_mcp.error_handlers import (
    create_validation_error_response,
    format_error_response,
    handle_external_api_error,
    map_repository_error,
)
from apigee_hybrid_mcp.exceptions import (
    AppError,
    AuthenticationError,
    ExternalServiceError,
    InvalidParameterError,
    ResourceAlreadyExistsError,
    ResourceNotFoundError,
)
from apigee_hybrid_mcp.repository.team_repository import (
    TeamAlreadyExistsError,
    TeamNotFoundError,
)


class TestFormatErrorResponse:
    """Test suite for format_error_response function."""

    def test_format_app_error(self) -> None:
        """Test formatting of AppError."""
        error = InvalidParameterError(
            parameter="email",
            value="",
            reason="must be valid email",
        )
        response = format_error_response(error, "create-user")

        assert len(response) == 1
        text = response[0].text
        assert "create-user" in text
        assert "INVALID_PARAMETER" in text
        assert "422" in text
        assert "must be valid email" in text
        assert error.correlation_id in text

    def test_format_authentication_error(self) -> None:
        """Test formatting of AuthenticationError."""
        error = AuthenticationError(message="Invalid token")
        response = format_error_response(error, "get-organization")

        text = response[0].text
        assert "AUTHENTICATION_ERROR" in text
        assert "401" in text
        assert "Invalid token" in text

    def test_format_generic_exception(self) -> None:
        """Test formatting of generic Python exception."""
        error = ValueError("Something went wrong")
        response = format_error_response(error, "test-operation")

        text = response[0].text
        assert "test-operation" in text
        assert "ValueError" in text
        assert "Something went wrong" in text
        assert "Unexpected Error" in text

    def test_format_generic_exception_with_traceback(self) -> None:
        """Test formatting with traceback included."""
        error = RuntimeError("Test error")
        response = format_error_response(
            error,
            "test-operation",
            include_traceback=True,
        )

        text = response[0].text
        assert "Stack Trace" in text or "Traceback" in text

    def test_format_error_with_details(self) -> None:
        """Test formatting error with detailed information."""
        error = ResourceNotFoundError(
            resource_type="team",
            resource_id="team-123",
            details={"searched_in": "database"},
        )
        response = format_error_response(error, "get-team")

        text = response[0].text
        assert "team" in text.lower()
        assert "team-123" in text
        assert "searched_in" in text or "database" in text


class TestHandleExternalApiError:
    """Test suite for handle_external_api_error function."""

    def test_handle_app_error_passthrough(self) -> None:
        """Test that AppErrors are passed through unchanged."""
        error = AuthenticationError(message="Auth failed")
        response = handle_external_api_error(error, "apigee_api", "list-proxies")

        text = response[0].text
        assert "AUTHENTICATION_ERROR" in text
        assert "Auth failed" in text

    def test_handle_generic_exception(self) -> None:
        """Test wrapping of generic exceptions."""
        error = ConnectionError("Connection refused")
        response = handle_external_api_error(error, "apigee_api", "list-proxies")

        text = response[0].text
        assert "EXTERNAL_SERVICE_ERROR" in text
        assert "apigee_api" in text
        assert "Connection refused" in text

    def test_handle_timeout_error(self) -> None:
        """Test handling of timeout errors."""
        import asyncio

        error = asyncio.TimeoutError()
        response = handle_external_api_error(error, "google_cloud", "get-token")

        text = response[0].text
        assert "EXTERNAL_SERVICE_ERROR" in text
        assert "google_cloud" in text


class TestCreateValidationErrorResponse:
    """Test suite for create_validation_error_response convenience function."""

    def test_create_validation_error(self) -> None:
        """Test creating a validation error response."""
        response = create_validation_error_response(
            parameter="timeout",
            reason="must be between 1 and 600",
            operation="create-debug-session",
        )

        text = response[0].text
        assert "timeout" in text
        assert "must be between 1 and 600" in text
        assert "create-debug-session" in text
        assert "INVALID_PARAMETER" in text


class TestMapRepositoryError:
    """Test suite for map_repository_error function."""

    def test_map_team_not_found_error(self) -> None:
        """Test mapping TeamNotFoundError to ResourceNotFoundError."""
        repo_error = TeamNotFoundError("team-123")
        mapped = map_repository_error(repo_error)

        assert isinstance(mapped, ResourceNotFoundError)
        assert mapped.details["resource_type"] == "team"
        assert mapped.details["resource_id"] == "team-123"

    def test_map_team_already_exists_error(self) -> None:
        """Test mapping TeamAlreadyExistsError to ResourceAlreadyExistsError."""
        repo_error = TeamAlreadyExistsError("engineering-team")
        mapped = map_repository_error(repo_error)

        assert isinstance(mapped, ResourceAlreadyExistsError)
        assert mapped.details["resource_type"] == "team"
        assert mapped.details["resource_id"] == "engineering-team"

    def test_map_app_error_passthrough(self) -> None:
        """Test that AppErrors pass through unchanged."""
        app_error = InvalidParameterError(
            parameter="test",
            value="",
            reason="test",
        )
        mapped = map_repository_error(app_error)

        assert mapped is app_error

    def test_map_generic_error(self) -> None:
        """Test mapping of generic exceptions."""
        generic_error = ValueError("Something went wrong")
        mapped = map_repository_error(generic_error)

        assert isinstance(mapped, ExternalServiceError)
        assert mapped.details["service"] == "repository"
        assert "ValueError" in mapped.details["error_type"]


class TestErrorResponseStructure:
    """Test error response structure and content."""

    def test_error_response_contains_correlation_id(self) -> None:
        """Test that all error responses contain correlation ID."""
        error = InvalidParameterError(
            parameter="test",
            value="",
            reason="test",
        )
        response = format_error_response(error, "test-operation")

        text = response[0].text
        assert "Correlation ID:" in text
        assert error.correlation_id in text

    def test_error_response_contains_error_code(self) -> None:
        """Test that error responses contain error code."""
        error = AuthenticationError()
        response = format_error_response(error, "test-operation")

        text = response[0].text
        assert "Error Code:" in text
        assert "AUTHENTICATION_ERROR" in text

    def test_error_response_contains_status(self) -> None:
        """Test that error responses contain HTTP status."""
        error = ResourceNotFoundError(
            resource_type="team",
            resource_id="123",
        )
        response = format_error_response(error, "test-operation")

        text = response[0].text
        assert "Status:" in text
        assert "404" in text

    def test_error_response_contains_message(self) -> None:
        """Test that error responses contain human-readable message."""
        error = InvalidParameterError(
            parameter="timeout",
            value="",
            reason="must be positive",
        )
        response = format_error_response(error, "test-operation")

        text = response[0].text
        assert "Message:" in text
        assert "timeout" in text
        assert "must be positive" in text

    def test_error_response_is_text_content(self) -> None:
        """Test that error responses use correct MCP type."""
        from mcp.types import TextContent

        error = AppError(message="Test")
        response = format_error_response(error, "test")

        assert len(response) == 1
        assert isinstance(response[0], TextContent)
        assert response[0].type == "text"


class TestMultipleErrorScenarios:
    """Test various error scenarios."""

    def test_missing_required_parameter(self) -> None:
        """Test error for missing required parameter."""
        from apigee_hybrid_mcp.exceptions import MissingParameterError

        error = MissingParameterError(parameter="organization")
        response = format_error_response(error, "list-environments")

        text = response[0].text
        assert "organization" in text
        assert "required" in text.lower()

    def test_expired_token(self) -> None:
        """Test error for expired token."""
        from apigee_hybrid_mcp.exceptions import ExpiredParameterError

        error = ExpiredParameterError(
            parameter="auth_token",
            expired_at="2024-01-01T00:00:00Z",
        )
        response = format_error_response(error, "api-request")

        text = response[0].text
        assert "auth_token" in text
        assert "expired" in text.lower()
        assert "2024-01-01" in text

    def test_authorization_denied(self) -> None:
        """Test error for authorization failure."""
        from apigee_hybrid_mcp.exceptions import AuthorizationError

        error = AuthorizationError(
            message="Insufficient permissions",
            resource="teams/admin",
        )
        response = format_error_response(error, "delete-team")

        text = response[0].text
        assert "403" in text
        assert "Insufficient permissions" in text
        assert "teams/admin" in text

    def test_external_service_unavailable(self) -> None:
        """Test error for external service failure."""
        error = ExternalServiceError(
            service="apigee_api",
            message="Service temporarily unavailable",
            status=503,
        )
        response = format_error_response(error, "create-proxy")

        text = response[0].text
        assert "503" in text
        assert "apigee_api" in text
        assert "temporarily unavailable" in text.lower()
