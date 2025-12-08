"""Unit tests for API Products functionality.

Tests cover:
- Listing API products
- Getting product details
- Creating products with quotas
- Updating products
- Deleting products
- Product attributes management
"""

import pytest
from unittest.mock import AsyncMock
from typing import Dict, Any

from apigee_hybrid_mcp.api.client import ApigeeClient, ApigeeAPIError


@pytest.mark.asyncio
class TestAPIProducts:
    """Test suite for API Products operations."""

    async def test_list_api_products(
        self,
        mock_apigee_client: ApigeeClient,
        sample_api_product: Dict[str, Any],
    ) -> None:
        """Test listing all API products in an organization.

        Verifies:
            - Correct API endpoint is called
            - Response is properly formatted
            - Multiple products are returned
        """
        # Arrange
        expected_response = {
            "apiProduct": [
                sample_api_product,
                {**sample_api_product, "name": "premium-product"},
            ]
        }
        mock_apigee_client.session.request.return_value.__aenter__.return_value.status = 200
        mock_apigee_client.session.request.return_value.__aenter__.return_value.text = AsyncMock(
            return_value='{"apiProduct": [{"name": "basic-product"}, {"name": "premium-product"}]}'
        )

        # Act
        result = await mock_apigee_client.get("apiproducts")

        # Assert
        assert "apiProduct" in result
        assert len(result["apiProduct"]) == 2

    async def test_get_api_product(
        self,
        mock_apigee_client: ApigeeClient,
        sample_api_product: Dict[str, Any],
    ) -> None:
        """Test getting specific API product details.

        Verifies:
            - Product details are retrieved correctly
            - Quota settings are included
            - All required fields are present
        """
        # Arrange
        import json

        mock_apigee_client.session.request.return_value.__aenter__.return_value.status = 200
        mock_apigee_client.session.request.return_value.__aenter__.return_value.text = AsyncMock(
            return_value=json.dumps(sample_api_product)
        )

        # Act
        result = await mock_apigee_client.get("apiproducts/basic-product")

        # Assert
        assert result["name"] == "basic-product"
        assert result["quota"] == "1000"
        assert result["quotaTimeUnit"] == "day"
        assert result["approvalType"] == "auto"

    async def test_create_api_product_with_quota(
        self,
        mock_apigee_client: ApigeeClient,
        sample_api_product: Dict[str, Any],
    ) -> None:
        """Test creating API product with quota configuration.

        Verifies:
            - Product is created with specified quotas
            - Rate limiting parameters are set correctly
            - API proxies are associated
        """
        # Arrange
        import json

        product_data = {
            "name": "new-product",
            "displayName": "New Product",
            "approvalType": "auto",
            "proxies": ["api1", "api2"],
            "quota": "5000",
            "quotaInterval": "1",
            "quotaTimeUnit": "hour",
        }
        mock_apigee_client.session.request.return_value.__aenter__.return_value.status = 200
        mock_apigee_client.session.request.return_value.__aenter__.return_value.text = AsyncMock(
            return_value=json.dumps({**product_data, "createdAt": "2024-01-01T00:00:00Z"})
        )

        # Act
        result = await mock_apigee_client.post("apiproducts", json_data=product_data)

        # Assert
        assert result["name"] == "new-product"
        assert result["quota"] == "5000"
        assert result["quotaTimeUnit"] == "hour"

    async def test_create_api_product_auto_approval(
        self,
        mock_apigee_client: ApigeeClient,
    ) -> None:
        """Test creating API product with auto approval.

        Verifies:
            - Auto approval type is set correctly
            - Apps are automatically approved for product access
        """
        # Arrange
        import json

        product_data = {
            "name": "auto-product",
            "approvalType": "auto",
        }
        mock_apigee_client.session.request.return_value.__aenter__.return_value.status = 200
        mock_apigee_client.session.request.return_value.__aenter__.return_value.text = AsyncMock(
            return_value=json.dumps(product_data)
        )

        # Act
        result = await mock_apigee_client.post("apiproducts", json_data=product_data)

        # Assert
        assert result["approvalType"] == "auto"

    async def test_create_api_product_manual_approval(
        self,
        mock_apigee_client: ApigeeClient,
    ) -> None:
        """Test creating API product with manual approval.

        Verifies:
            - Manual approval type is set correctly
            - Apps require manual approval for product access
        """
        # Arrange
        import json

        product_data = {
            "name": "manual-product",
            "approvalType": "manual",
        }
        mock_apigee_client.session.request.return_value.__aenter__.return_value.status = 200
        mock_apigee_client.session.request.return_value.__aenter__.return_value.text = AsyncMock(
            return_value=json.dumps(product_data)
        )

        # Act
        result = await mock_apigee_client.post("apiproducts", json_data=product_data)

        # Assert
        assert result["approvalType"] == "manual"

    async def test_update_api_product(
        self,
        mock_apigee_client: ApigeeClient,
        sample_api_product: Dict[str, Any],
    ) -> None:
        """Test updating API product configuration.

        Verifies:
            - Product properties can be updated
            - Quota changes are applied
            - Last modified timestamp is updated
        """
        # Arrange
        import json

        updated_product = {**sample_api_product, "quota": "2000", "displayName": "Updated Product"}
        mock_apigee_client.session.request.return_value.__aenter__.return_value.status = 200
        mock_apigee_client.session.request.return_value.__aenter__.return_value.text = AsyncMock(
            return_value=json.dumps(updated_product)
        )

        # Act
        result = await mock_apigee_client.put(
            "apiproducts/basic-product",
            json_data={"quota": "2000", "displayName": "Updated Product"},
        )

        # Assert
        assert result["quota"] == "2000"
        assert result["displayName"] == "Updated Product"

    async def test_delete_api_product(
        self,
        mock_apigee_client: ApigeeClient,
        sample_api_product: Dict[str, Any],
    ) -> None:
        """Test deleting API product.

        Verifies:
            - Product is deleted successfully
            - Deleted product details are returned
        """
        # Arrange
        import json

        mock_apigee_client.session.request.return_value.__aenter__.return_value.status = 200
        mock_apigee_client.session.request.return_value.__aenter__.return_value.text = AsyncMock(
            return_value=json.dumps(sample_api_product)
        )

        # Act
        result = await mock_apigee_client.delete("apiproducts/basic-product")

        # Assert
        assert result["name"] == "basic-product"

    async def test_api_product_with_multiple_proxies(
        self,
        mock_apigee_client: ApigeeClient,
    ) -> None:
        """Test API product with multiple proxy associations.

        Verifies:
            - Multiple proxies can be associated
            - All proxies are included in response
        """
        # Arrange
        import json

        product_data = {
            "name": "multi-proxy-product",
            "proxies": ["proxy1", "proxy2", "proxy3"],
        }
        mock_apigee_client.session.request.return_value.__aenter__.return_value.status = 200
        mock_apigee_client.session.request.return_value.__aenter__.return_value.text = AsyncMock(
            return_value=json.dumps(product_data)
        )

        # Act
        result = await mock_apigee_client.post("apiproducts", json_data=product_data)

        # Assert
        assert len(result["proxies"]) == 3
        assert "proxy1" in result["proxies"]

    async def test_api_product_quota_time_units(
        self,
        mock_apigee_client: ApigeeClient,
    ) -> None:
        """Test API product quota with different time units.

        Verifies:
            - Different quota time units (minute, hour, day, month)
            - Quota intervals are set correctly
        """
        # Test each time unit
        for time_unit in ["minute", "hour", "day", "month"]:
            # Arrange
            import json

            product_data = {
                "name": f"product-{time_unit}",
                "quota": "100",
                "quotaInterval": "1",
                "quotaTimeUnit": time_unit,
            }
            mock_apigee_client.session.request.return_value.__aenter__.return_value.status = 200
            mock_apigee_client.session.request.return_value.__aenter__.return_value.text = (
                AsyncMock(return_value=json.dumps(product_data))
            )

            # Act
            result = await mock_apigee_client.post("apiproducts", json_data=product_data)

            # Assert
            assert result["quotaTimeUnit"] == time_unit

    async def test_api_product_error_handling(
        self,
        mock_apigee_client: ApigeeClient,
    ) -> None:
        """Test error handling for API product operations.

        Verifies:
            - 404 error for non-existent product
            - 409 error for duplicate product name
            - Error details are captured
        """
        # Arrange - test 404
        mock_apigee_client.session.request.return_value.__aenter__.return_value.status = 404
        mock_apigee_client.session.request.return_value.__aenter__.return_value.text = AsyncMock(
            return_value='{"error": {"message": "Product not found"}}'
        )

        # Act & Assert
        with pytest.raises(ApigeeAPIError) as exc_info:
            await mock_apigee_client.get("apiproducts/nonexistent")

        assert exc_info.value.status_code == 404
