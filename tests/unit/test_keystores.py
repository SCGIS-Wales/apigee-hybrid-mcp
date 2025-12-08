"""Unit tests for Keystore and Truststore management.

Tests cover:
- Listing keystores
- Getting keystore details
- Creating keystores
- Listing keystore aliases (certificates)
- Getting alias details
- Certificate management
"""

import pytest
from unittest.mock import AsyncMock
from typing import Dict, Any

from apigee_hybrid_mcp.api.client import ApigeeClient


@pytest.mark.asyncio
class TestKeystoreManagement:
    """Test suite for Keystore and certificate management."""
    
    async def test_list_keystores(
        self,
        mock_apigee_client: ApigeeClient,
    ) -> None:
        """Test listing all keystores in an environment."""
        # Arrange
        import json
        keystores_response = {"keystores": ["tls-keystore", "truststore"]}
        mock_apigee_client.session.request.return_value.__aenter__.return_value.status = 200
        mock_apigee_client.session.request.return_value.__aenter__.return_value.text = AsyncMock(
            return_value=json.dumps(keystores_response)
        )
        
        # Act
        result = await mock_apigee_client.get("environments/prod/keystores")
        
        # Assert
        assert "keystores" in result
        assert len(result["keystores"]) == 2
        
    async def test_get_keystore_with_aliases(
        self,
        mock_apigee_client: ApigeeClient,
        sample_keystore: Dict[str, Any],
    ) -> None:
        """Test getting keystore details including aliases."""
        # Arrange
        import json
        mock_apigee_client.session.request.return_value.__aenter__.return_value.status = 200
        mock_apigee_client.session.request.return_value.__aenter__.return_value.text = AsyncMock(
            return_value=json.dumps(sample_keystore)
        )
        
        # Act
        result = await mock_apigee_client.get("environments/prod/keystores/tls-keystore")
        
        # Assert
        assert result["name"] == "tls-keystore"
        assert "aliases" in result
        assert len(result["aliases"]) == 2
        
    async def test_get_keystore_alias_certificate(
        self,
        mock_apigee_client: ApigeeClient,
        sample_keystore_alias: Dict[str, Any],
    ) -> None:
        """Test getting certificate details for a keystore alias."""
        # Arrange
        import json
        mock_apigee_client.session.request.return_value.__aenter__.return_value.status = 200
        mock_apigee_client.session.request.return_value.__aenter__.return_value.text = AsyncMock(
            return_value=json.dumps(sample_keystore_alias)
        )
        
        # Act
        result = await mock_apigee_client.get(
            "environments/prod/keystores/tls-keystore/aliases/cert1"
        )
        
        # Assert
        assert result["alias"] == "cert1"
        assert result["type"] == "keycert"
        assert "certsInfo" in result
        cert_info = result["certsInfo"]["certInfo"][0]
        assert cert_info["isValid"] == "true"
        assert "api.example.com" in cert_info["subjectAlternativeNames"]
