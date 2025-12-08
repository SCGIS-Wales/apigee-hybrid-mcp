"""Unit tests for Debug Sessions (Trace) functionality.

Tests cover:
- Creating debug sessions
- Getting debug session data
- Listing captured transactions
- Trace data analysis
"""

import pytest
from unittest.mock import AsyncMock
from typing import Dict, Any

from apigee_hybrid_mcp.api.client import ApigeeClient


@pytest.mark.asyncio
class TestDebugSessions:
    """Test suite for Debug Sessions (Trace) operations."""

    async def test_create_debug_session(
        self,
        mock_apigee_client: ApigeeClient,
        sample_debug_session: Dict[str, Any],
    ) -> None:
        """Test creating a debug session for an API proxy."""
        # Arrange
        import json

        mock_apigee_client.session.request.return_value.__aenter__.return_value.status = 200
        mock_apigee_client.session.request.return_value.__aenter__.return_value.text = AsyncMock(
            return_value=json.dumps(sample_debug_session)
        )

        # Act
        result = await mock_apigee_client.post(
            "environments/prod/apis/weather-api/revisions/1/debugsessions",
            params={"session": "session-12345", "timeout": "300"},
        )

        # Assert
        assert result["name"] == "session-12345"
        assert result["timeout"] == "300"

    async def test_get_debug_session_trace_data(
        self,
        mock_apigee_client: ApigeeClient,
        sample_trace_data: Dict[str, Any],
    ) -> None:
        """Test getting trace data from a debug session."""
        # Arrange
        import json

        mock_apigee_client.session.request.return_value.__aenter__.return_value.status = 200
        mock_apigee_client.session.request.return_value.__aenter__.return_value.text = AsyncMock(
            return_value=json.dumps(sample_trace_data)
        )

        # Act
        result = await mock_apigee_client.get(
            "environments/prod/apis/weather-api/revisions/1/debugsessions/session-12345/data"
        )

        # Assert
        assert result["completed"] is True
        assert len(result["point"]) > 0
        assert result["point"][0]["results"]["ActionResult"] == "success"
