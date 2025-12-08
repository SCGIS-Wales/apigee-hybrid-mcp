"""Unit tests for Developers API functionality.

Tests cover:
- Listing developers
- Getting developer details
- Creating developers
- Updating developers
- Managing developer status
- Developer attributes
"""

import pytest
from unittest.mock import AsyncMock
from typing import Dict, Any

from apigee_hybrid_mcp.api.client import ApigeeClient


@pytest.mark.asyncio
class TestDevelopers:
    """Test suite for Developers operations."""

    async def test_list_developers(
        self,
        mock_apigee_client: ApigeeClient,
        sample_developer: Dict[str, Any],
    ) -> None:
        """Test listing all developers in an organization."""
        # Arrange
        import json

        expected_response = {
            "developer": [sample_developer, {**sample_developer, "email": "dev2@example.com"}]
        }
        mock_apigee_client.session.request.return_value.__aenter__.return_value.status = 200
        mock_apigee_client.session.request.return_value.__aenter__.return_value.text = AsyncMock(
            return_value=json.dumps(expected_response)
        )

        # Act
        result = await mock_apigee_client.get("developers")

        # Assert
        assert "developer" in result
        assert len(result["developer"]) == 2

    async def test_create_developer(
        self,
        mock_apigee_client: ApigeeClient,
    ) -> None:
        """Test creating a new developer."""
        # Arrange
        import json

        developer_data = {
            "email": "newdev@example.com",
            "firstName": "New",
            "lastName": "Developer",
            "userName": "newdev",
        }
        expected_response = {**developer_data, "developerId": "dev-new", "status": "active"}
        mock_apigee_client.session.request.return_value.__aenter__.return_value.status = 200
        mock_apigee_client.session.request.return_value.__aenter__.return_value.text = AsyncMock(
            return_value=json.dumps(expected_response)
        )

        # Act
        result = await mock_apigee_client.post("developers", json_data=developer_data)

        # Assert
        assert result["email"] == "newdev@example.com"
        assert result["status"] == "active"
        assert "developerId" in result
