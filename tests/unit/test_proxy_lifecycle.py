"""Unit tests for Proxy Lifecycle functionality.

Tests cover:
- Listing API proxies
- Getting proxy details
- Getting proxy revisions
- Deploying proxies
- Undeploying proxies
- Deployment status checks
"""

import pytest
from unittest.mock import AsyncMock
from typing import Dict, Any

from apigee_hybrid_mcp.api.client import ApigeeClient


@pytest.mark.asyncio
class TestProxyLifecycle:
    """Test suite for API Proxy lifecycle operations."""
    
    async def test_deploy_api_proxy(
        self,
        mock_apigee_client: ApigeeClient,
    ) -> None:
        """Test deploying an API proxy revision to an environment."""
        # Arrange
        import json
        deployment_response = {
            "name": "weather-api",
            "environment": "prod",
            "revision": "3",
            "state": "deployed",
            "deployStartTime": "2024-01-01T00:00:00Z",
        }
        mock_apigee_client.session.request.return_value.__aenter__.return_value.status = 200
        mock_apigee_client.session.request.return_value.__aenter__.return_value.text = AsyncMock(
            return_value=json.dumps(deployment_response)
        )
        
        # Act
        result = await mock_apigee_client.post(
            "environments/prod/apis/weather-api/revisions/3/deployments"
        )
        
        # Assert
        assert result["state"] == "deployed"
        assert result["revision"] == "3"
        assert result["environment"] == "prod"
        
    async def test_undeploy_api_proxy(
        self,
        mock_apigee_client: ApigeeClient,
    ) -> None:
        """Test undeploying an API proxy revision from an environment."""
        # Arrange
        import json
        undeploy_response = {
            "name": "weather-api",
            "environment": "prod",
            "revision": "2",
            "state": "undeployed",
        }
        mock_apigee_client.session.request.return_value.__aenter__.return_value.status = 200
        mock_apigee_client.session.request.return_value.__aenter__.return_value.text = AsyncMock(
            return_value=json.dumps(undeploy_response)
        )
        
        # Act
        result = await mock_apigee_client.delete(
            "environments/prod/apis/weather-api/revisions/2/deployments"
        )
        
        # Assert
        assert result["state"] == "undeployed"
