"""Pytest configuration and fixtures for Apigee Hybrid MCP tests.

This module provides shared fixtures and configuration for all tests.
Fixtures are organized by scope and category for efficient test execution.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from typing import AsyncGenerator, Dict, Any

from apigee_hybrid_mcp.config import Settings, get_settings
from apigee_hybrid_mcp.api.client import ApigeeClient


@pytest.fixture(scope="session")
def test_settings() -> Settings:
    """Provide test settings with mock configuration.
    
    Returns:
        Settings: Test configuration with dummy values
    """
    return Settings(
        google_project_id="test-project",
        google_credentials_path=None,
        apigee_organization="test-org",
        apigee_api_base_url="https://apigee.googleapis.com/v1",
        log_level="DEBUG",
        max_retries=3,
        request_timeout=30,
    )


@pytest.fixture
def mock_credentials() -> MagicMock:
    """Mock Google Cloud credentials.
    
    Returns:
        MagicMock: Mocked credentials with valid token
    """
    creds = MagicMock()
    creds.valid = True
    creds.token = "mock-token-12345"
    return creds


@pytest.fixture
async def mock_apigee_client(test_settings: Settings, mock_credentials: MagicMock) -> AsyncGenerator[ApigeeClient, None]:
    """Provide mocked Apigee API client.
    
    Args:
        test_settings: Test configuration
        mock_credentials: Mocked credentials
        
    Yields:
        ApigeeClient: Client with mocked HTTP session
    """
    with patch("apigee_hybrid_mcp.api.client.service_account"):
        client = ApigeeClient(test_settings)
        client.credentials = mock_credentials
        
        # Mock aiohttp session
        mock_session = AsyncMock()
        client.session = mock_session
        
        yield client


@pytest.fixture
def sample_organization() -> Dict[str, Any]:
    """Sample organization response data.
    
    Returns:
        Dict: Organization data structure
    """
    return {
        "name": "organizations/test-org",
        "displayName": "Test Organization",
        "description": "Test organization for unit tests",
        "createdAt": "2024-01-01T00:00:00Z",
        "lastModifiedAt": "2024-01-01T00:00:00Z",
        "environments": ["dev", "test", "prod"],
        "runtimeType": "HYBRID",
    }


@pytest.fixture
def sample_environment() -> Dict[str, Any]:
    """Sample environment response data.
    
    Returns:
        Dict: Environment data structure
    """
    return {
        "name": "prod",
        "displayName": "Production",
        "description": "Production environment",
        "type": "PRODUCTION",
        "state": "ACTIVE",
        "createdAt": "2024-01-01T00:00:00Z",
        "lastModifiedAt": "2024-01-01T00:00:00Z",
    }


@pytest.fixture
def sample_api_proxy() -> Dict[str, Any]:
    """Sample API proxy response data.
    
    Returns:
        Dict: API proxy data structure
    """
    return {
        "name": "weather-api",
        "revision": ["1", "2", "3"],
        "metaData": {
            "createdAt": "2024-01-01T00:00:00Z",
            "lastModifiedAt": "2024-01-01T00:00:00Z",
        },
    }


@pytest.fixture
def sample_developer() -> Dict[str, Any]:
    """Sample developer response data.
    
    Returns:
        Dict: Developer data structure
    """
    return {
        "email": "dev@example.com",
        "firstName": "John",
        "lastName": "Doe",
        "userName": "jdoe",
        "developerId": "dev-12345",
        "status": "active",
        "createdAt": "2024-01-01T00:00:00Z",
        "lastModifiedAt": "2024-01-01T00:00:00Z",
        "apps": ["app1", "app2"],
    }


@pytest.fixture
def sample_developer_app() -> Dict[str, Any]:
    """Sample developer app response data.
    
    Returns:
        Dict: Developer app data structure
    """
    return {
        "name": "mobile-app",
        "appId": "app-12345",
        "developerId": "dev-12345",
        "status": "approved",
        "apiProducts": ["basic-product"],
        "credentials": [
            {
                "consumerKey": "key-12345",
                "consumerSecret": "secret-12345",
                "status": "approved",
                "expiresAt": "-1",
                "issuedAt": "1704067200000",
                "apiProducts": [
                    {
                        "apiproduct": "basic-product",
                        "status": "approved",
                    }
                ],
            }
        ],
        "createdAt": "2024-01-01T00:00:00Z",
        "lastModifiedAt": "2024-01-01T00:00:00Z",
    }


@pytest.fixture
def sample_api_product() -> Dict[str, Any]:
    """Sample API product response data.
    
    Returns:
        Dict: API product data structure
    """
    return {
        "name": "basic-product",
        "displayName": "Basic Product",
        "description": "Basic tier API product",
        "approvalType": "auto",
        "apiResources": ["/**"],
        "proxies": ["weather-api", "maps-api"],
        "environments": ["prod"],
        "quota": "1000",
        "quotaInterval": "1",
        "quotaTimeUnit": "day",
        "createdAt": "2024-01-01T00:00:00Z",
        "lastModifiedAt": "2024-01-01T00:00:00Z",
    }


@pytest.fixture
def sample_shared_flow() -> Dict[str, Any]:
    """Sample shared flow response data.
    
    Returns:
        Dict: Shared flow data structure
    """
    return {
        "name": "security-flow",
        "revision": ["1", "2"],
        "metaData": {
            "createdAt": "2024-01-01T00:00:00Z",
            "lastModifiedAt": "2024-01-01T00:00:00Z",
        },
    }


@pytest.fixture
def sample_keystore() -> Dict[str, Any]:
    """Sample keystore response data.
    
    Returns:
        Dict: Keystore data structure
    """
    return {
        "name": "tls-keystore",
        "aliases": ["cert1", "cert2"],
    }


@pytest.fixture
def sample_keystore_alias() -> Dict[str, Any]:
    """Sample keystore alias response data.
    
    Returns:
        Dict: Keystore alias data structure
    """
    return {
        "alias": "cert1",
        "type": "keycert",
        "certsInfo": {
            "certInfo": [
                {
                    "version": "3",
                    "subject": "CN=api.example.com",
                    "issuer": "CN=Test CA",
                    "serialNumber": "12345",
                    "notBefore": "2024-01-01T00:00:00Z",
                    "notAfter": "2025-01-01T00:00:00Z",
                    "isValid": "true",
                    "subjectAlternativeNames": ["api.example.com", "www.example.com"],
                }
            ],
        },
    }


@pytest.fixture
def sample_company() -> Dict[str, Any]:
    """Sample company (team) response data.
    
    Returns:
        Dict: Company data structure
    """
    return {
        "name": "acme-corp",
        "displayName": "ACME Corporation",
        "organizationName": "test-org",
        "status": "active",
        "apps": ["enterprise-app"],
        "createdAt": "2024-01-01T00:00:00Z",
        "lastModifiedAt": "2024-01-01T00:00:00Z",
    }


@pytest.fixture
def sample_debug_session() -> Dict[str, Any]:
    """Sample debug session response data.
    
    Returns:
        Dict: Debug session data structure
    """
    return {
        "name": "session-12345",
        "timeout": "300",
        "count": "5",
        "createTime": "2024-01-01T00:00:00Z",
    }


@pytest.fixture
def sample_trace_data() -> Dict[str, Any]:
    """Sample trace transaction data.
    
    Returns:
        Dict: Trace data structure
    """
    return {
        "point": [
            {
                "id": "point-1",
                "results": {
                    "ActionResult": "success",
                    "timestamp": "2024-01-01T00:00:00Z",
                    "pipelineMessage": {
                        "headers": [{"name": "Content-Type", "value": "application/json"}],
                        "method": "GET",
                        "path": "/weather",
                        "statusCode": "200",
                        "reasonPhrase": "OK",
                    },
                },
            }
        ],
        "completed": True,
    }
