"""Unit tests for parameter validation and redaction.

Tests cover:
- Parameter validators
- Sensitive field redaction
- Validation decorators
- Pydantic model validation
"""

from datetime import datetime, timezone

import pytest

from apigee_hybrid_mcp.exceptions import (
    ExpiredParameterError,
    InvalidParameterError,
    MissingParameterError,
)
from apigee_hybrid_mcp.validation import (
    ParameterValidator,
    redact_sensitive_fields,
    validate_parameters,
)


class TestRedactSensitiveFields:
    """Test suite for sensitive field redaction."""

    def test_redact_token_field(self) -> None:
        """Test redaction of token field."""
        data = {"username": "user@example.com", "token": "secret-token-123"}
        redacted = redact_sensitive_fields(data)
        assert redacted["username"] == "user@example.com"
        assert redacted["token"] == "***REDACTED***"

    def test_redact_password_field(self) -> None:
        """Test redaction of password field."""
        data = {"username": "admin", "password": "super-secret"}
        redacted = redact_sensitive_fields(data)
        assert redacted["username"] == "admin"
        assert redacted["password"] == "***REDACTED***"

    def test_redact_multiple_sensitive_fields(self) -> None:
        """Test redaction of multiple sensitive fields."""
        data = {
            "user": "admin",
            "password": "pass123",
            "api_key": "key123",
            "auth_token": "token123",
        }
        redacted = redact_sensitive_fields(data)
        assert redacted["user"] == "admin"
        assert redacted["password"] == "***REDACTED***"
        assert redacted["api_key"] == "***REDACTED***"
        assert redacted["auth_token"] == "***REDACTED***"

    def test_redact_nested_dict(self) -> None:
        """Test redaction in nested dictionaries."""
        data = {
            "user": "admin",
            "settings": {"password": "secret", "token": "abc123", "theme": "dark"},
        }
        redacted = redact_sensitive_fields(data)
        assert redacted["user"] == "admin"
        assert redacted["settings"]["password"] == "***REDACTED***"
        assert redacted["settings"]["token"] == "***REDACTED***"
        assert redacted["settings"]["theme"] == "dark"  # Non-sensitive field preserved

    def test_redact_in_list(self) -> None:
        """Test redaction in lists containing dicts."""
        data = {
            "users": [
                {"name": "user1", "password": "pass1"},
                {"name": "user2", "password": "pass2"},
            ]
        }
        redacted = redact_sensitive_fields(data)
        assert redacted["users"][0]["name"] == "user1"
        assert redacted["users"][0]["password"] == "***REDACTED***"
        assert redacted["users"][1]["name"] == "user2"
        assert redacted["users"][1]["password"] == "***REDACTED***"

    def test_no_sensitive_fields(self) -> None:
        """Test that non-sensitive data is not modified."""
        data = {"name": "John", "email": "john@example.com", "age": 30}
        redacted = redact_sensitive_fields(data)
        assert redacted == data

    def test_case_insensitive_redaction(self) -> None:
        """Test that redaction is case-insensitive."""
        data = {"PASSWORD": "secret", "Token": "abc123", "API_KEY": "key123"}
        redacted = redact_sensitive_fields(data)
        assert redacted["PASSWORD"] == "***REDACTED***"
        assert redacted["Token"] == "***REDACTED***"
        assert redacted["API_KEY"] == "***REDACTED***"


class TestParameterValidator:
    """Test suite for ParameterValidator utility class."""

    def test_validate_non_empty_string_valid(self) -> None:
        """Test non-empty string validation with valid input."""
        result = ParameterValidator.validate_non_empty_string("test", "param")
        assert result == "test"

    def test_validate_non_empty_string_invalid_type(self) -> None:
        """Test non-empty string validation with non-string."""
        with pytest.raises(InvalidParameterError) as exc_info:
            ParameterValidator.validate_non_empty_string(123, "param")
        assert exc_info.value.details["parameter"] == "param"
        assert "must be a string" in exc_info.value.details["reason"]

    def test_validate_non_empty_string_empty(self) -> None:
        """Test non-empty string validation with empty string."""
        with pytest.raises(InvalidParameterError) as exc_info:
            ParameterValidator.validate_non_empty_string("   ", "param")
        assert "must not be empty" in exc_info.value.details["reason"]

    def test_validate_positive_integer_valid(self) -> None:
        """Test positive integer validation with valid input."""
        result = ParameterValidator.validate_positive_integer(42, "count")
        assert result == 42

    def test_validate_positive_integer_invalid_type(self) -> None:
        """Test positive integer validation with non-integer."""
        with pytest.raises(InvalidParameterError) as exc_info:
            ParameterValidator.validate_positive_integer("42", "count")
        assert "must be an integer" in exc_info.value.details["reason"]

    def test_validate_positive_integer_zero(self) -> None:
        """Test positive integer validation with zero."""
        with pytest.raises(InvalidParameterError) as exc_info:
            ParameterValidator.validate_positive_integer(0, "count")
        assert "must be positive" in exc_info.value.details["reason"]

    def test_validate_positive_integer_negative(self) -> None:
        """Test positive integer validation with negative number."""
        with pytest.raises(InvalidParameterError) as exc_info:
            ParameterValidator.validate_positive_integer(-5, "count")
        assert "must be positive" in exc_info.value.details["reason"]

    def test_validate_email_valid(self) -> None:
        """Test email validation with valid addresses."""
        valid_emails = [
            "user@example.com",
            "test.user@example.co.uk",
            "admin+tag@example.org",
        ]
        for email in valid_emails:
            result = ParameterValidator.validate_email(email, "email")
            assert result == email

    def test_validate_email_invalid(self) -> None:
        """Test email validation with invalid addresses."""
        invalid_emails = ["not-an-email", "@example.com", "user@", "user@.com"]
        for email in invalid_emails:
            with pytest.raises(InvalidParameterError):
                ParameterValidator.validate_email(email, "email")

    def test_validate_pattern_valid(self) -> None:
        """Test pattern validation with matching input."""
        result = ParameterValidator.validate_pattern(
            "test-123",
            "name",
            r"^[a-z0-9-]+$",
            "lowercase alphanumeric with hyphens",
        )
        assert result == "test-123"

    def test_validate_pattern_invalid(self) -> None:
        """Test pattern validation with non-matching input."""
        with pytest.raises(InvalidParameterError) as exc_info:
            ParameterValidator.validate_pattern(
                "Test-123!",
                "name",
                r"^[a-z0-9-]+$",
                "lowercase alphanumeric with hyphens",
            )
        assert "must match pattern" in exc_info.value.details["reason"]

    def test_validate_in_range_valid(self) -> None:
        """Test range validation with value in range."""
        result = ParameterValidator.validate_in_range(50, "timeout", 1, 100)
        assert result == 50

    def test_validate_in_range_below_min(self) -> None:
        """Test range validation with value below minimum."""
        with pytest.raises(InvalidParameterError) as exc_info:
            ParameterValidator.validate_in_range(0, "timeout", 1, 100)
        assert "must be at least 1" in exc_info.value.details["reason"]

    def test_validate_in_range_above_max(self) -> None:
        """Test range validation with value above maximum."""
        with pytest.raises(InvalidParameterError) as exc_info:
            ParameterValidator.validate_in_range(101, "timeout", 1, 100)
        assert "must be at most 100" in exc_info.value.details["reason"]

    def test_validate_in_range_min_only(self) -> None:
        """Test range validation with only minimum."""
        result = ParameterValidator.validate_in_range(1000, "value", min_val=1)
        assert result == 1000

    def test_validate_in_range_max_only(self) -> None:
        """Test range validation with only maximum."""
        result = ParameterValidator.validate_in_range(50, "value", max_val=100)
        assert result == 50

    def test_validate_enum_valid(self) -> None:
        """Test enum validation with valid value."""
        result = ParameterValidator.validate_enum("prod", "environment", ["dev", "staging", "prod"])
        assert result == "prod"

    def test_validate_enum_invalid(self) -> None:
        """Test enum validation with invalid value."""
        with pytest.raises(InvalidParameterError) as exc_info:
            ParameterValidator.validate_enum("invalid", "environment", ["dev", "staging", "prod"])
        assert "must be one of" in exc_info.value.details["reason"]

    def test_validate_not_expired_valid(self) -> None:
        """Test expiration validation with future timestamp."""
        future_time = datetime(2099, 12, 31, 23, 59, 59, tzinfo=timezone.utc)
        future_iso = future_time.isoformat()
        # Should not raise
        ParameterValidator.validate_not_expired(future_iso, "token")

    def test_validate_not_expired_expired(self) -> None:
        """Test expiration validation with past timestamp."""
        past_time = datetime(2000, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        past_iso = past_time.isoformat()
        with pytest.raises(ExpiredParameterError) as exc_info:
            ParameterValidator.validate_not_expired(past_iso, "token")
        assert exc_info.value.details["parameter"] == "token"

    def test_validate_not_expired_invalid_format(self) -> None:
        """Test expiration validation with invalid timestamp format."""
        with pytest.raises(InvalidParameterError) as exc_info:
            ParameterValidator.validate_not_expired("not-a-timestamp", "token")
        assert "must be valid ISO 8601 timestamp" in exc_info.value.details["reason"]

    def test_validate_list_not_empty_valid(self) -> None:
        """Test non-empty list validation with valid input."""
        result = ParameterValidator.validate_list_not_empty([1, 2, 3], "items")
        assert result == [1, 2, 3]

    def test_validate_list_not_empty_empty(self) -> None:
        """Test non-empty list validation with empty list."""
        with pytest.raises(InvalidParameterError) as exc_info:
            ParameterValidator.validate_list_not_empty([], "items")
        assert "must not be empty" in exc_info.value.details["reason"]

    def test_validate_list_not_empty_invalid_type(self) -> None:
        """Test non-empty list validation with non-list."""
        with pytest.raises(InvalidParameterError) as exc_info:
            ParameterValidator.validate_list_not_empty("not-a-list", "items")
        assert "must be a list" in exc_info.value.details["reason"]

    def test_validate_unique_items_valid(self) -> None:
        """Test unique items validation with unique list."""
        result = ParameterValidator.validate_unique_items([1, 2, 3], "items")
        assert result == [1, 2, 3]

    def test_validate_unique_items_duplicates(self) -> None:
        """Test unique items validation with duplicates."""
        with pytest.raises(InvalidParameterError) as exc_info:
            ParameterValidator.validate_unique_items([1, 2, 2, 3], "items")
        assert "must contain unique items" in exc_info.value.details["reason"]


class TestValidateParametersDecorator:
    """Test suite for @validate_parameters decorator."""

    @pytest.mark.asyncio
    async def test_decorator_with_all_required_params(self) -> None:
        """Test decorator passes when all required params present."""

        @validate_parameters(required=["org", "env"])
        async def test_func(arguments: dict) -> str:
            return "success"

        result = await test_func(arguments={"org": "test-org", "env": "prod"})
        assert result == "success"

    @pytest.mark.asyncio
    async def test_decorator_missing_required_param(self) -> None:
        """Test decorator raises when required param missing."""

        @validate_parameters(required=["org", "env"])
        async def test_func(arguments: dict) -> str:
            return "success"

        with pytest.raises(MissingParameterError) as exc_info:
            await test_func(arguments={"org": "test-org"})

        assert exc_info.value.details["parameter"] == "env"

    @pytest.mark.asyncio
    async def test_decorator_none_value_treated_as_missing(self) -> None:
        """Test decorator treats None as missing parameter."""

        @validate_parameters(required=["org"])
        async def test_func(arguments: dict) -> str:
            return "success"

        with pytest.raises(MissingParameterError):
            await test_func(arguments={"org": None})

    @pytest.mark.asyncio
    async def test_decorator_no_required_params(self) -> None:
        """Test decorator with no required parameters."""

        @validate_parameters()
        async def test_func(arguments: dict) -> str:
            return "success"

        result = await test_func(arguments={})
        assert result == "success"

    @pytest.mark.asyncio
    async def test_decorator_with_extra_params(self) -> None:
        """Test decorator allows extra parameters."""

        @validate_parameters(required=["org"])
        async def test_func(arguments: dict) -> str:
            return f"org={arguments['org']}, env={arguments.get('env', 'default')}"

        result = await test_func(arguments={"org": "test-org", "env": "prod"})
        assert result == "org=test-org, env=prod"
