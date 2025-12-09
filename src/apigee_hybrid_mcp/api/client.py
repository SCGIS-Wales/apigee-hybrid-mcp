"""Base API client for Apigee Hybrid with authentication and error handling."""

import asyncio
import json
from typing import Any, Optional

import aiohttp
from google.auth.transport.requests import Request
from google.oauth2 import service_account

from apigee_hybrid_mcp.config import Settings
from apigee_hybrid_mcp.exceptions import (
    AppError,
    AuthenticationError,
    ExternalServiceError,
    TimeoutError as AppTimeoutError,
)
from apigee_hybrid_mcp.utils.logging import get_logger
from apigee_hybrid_mcp.utils.resilience import RateLimiter, create_circuit_breaker

logger = get_logger(__name__)

# Constants for response handling
MAX_RESPONSE_LOG_LENGTH = 500  # Maximum characters to log from error responses
MAX_RESPONSE_DETAIL_LENGTH = 200  # Maximum characters for error details


# Keep legacy exception for backward compatibility
class ApigeeAPIError(Exception):
    """Base exception for Apigee API errors.

    Deprecated: Use exceptions from apigee_hybrid_mcp.exceptions instead.
    This class is maintained for backward compatibility only.
    """

    def __init__(
        self, message: str, status_code: Optional[int] = None, response_body: Optional[str] = None
    ):
        """Initialize the API error.

        Args:
            message: Error message
            status_code: HTTP status code if available
            response_body: Response body if available
        """
        self.message = message
        self.status_code = status_code
        self.response_body = response_body
        super().__init__(self.message)


class ApigeeClient:
    """Base client for interacting with Apigee Hybrid APIs."""

    def __init__(self, settings: Settings):
        """Initialize the Apigee client.

        Args:
            settings: Application settings
        """
        self.settings = settings
        self.base_url = settings.apigee_api_base_url
        self.organization = settings.apigee_organization
        self.session: Optional[aiohttp.ClientSession] = None
        self.credentials: Optional[service_account.Credentials] = None
        self.rate_limiter = RateLimiter(
            settings.rate_limit_requests,
            settings.rate_limit_window,
        )
        self.circuit_breaker = create_circuit_breaker(
            failure_threshold=settings.circuit_breaker_failure_threshold,
            timeout_duration=settings.circuit_breaker_timeout,
            name="apigee_api",
        )

        # Initialize credentials
        if settings.google_credentials_path:
            self.credentials = service_account.Credentials.from_service_account_file(
                settings.google_credentials_path,
                scopes=["https://www.googleapis.com/auth/cloud-platform"],
            )

    async def __aenter__(self) -> "ApigeeClient":
        """Async context manager entry."""
        timeout = aiohttp.ClientTimeout(total=self.settings.request_timeout)
        self.session = aiohttp.ClientSession(timeout=timeout)
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        if self.session:
            await self.session.close()

    def _get_auth_token(self) -> str:
        """Get authentication token.

        Returns:
            Bearer token for API requests

        Raises:
            AuthenticationError: If credentials are not configured or invalid
        """
        if not self.credentials:
            raise AuthenticationError(
                message="Google Cloud credentials not configured",
                details={"reason": "credentials_path_not_set"},
            )

        try:
            if not self.credentials.valid:
                self.credentials.refresh(Request())
        except Exception as e:
            raise AuthenticationError(
                message="Failed to refresh authentication token",
                details={"reason": str(e)},
            )

        token = self.credentials.token
        if token is None:
            raise AuthenticationError(
                message="Failed to obtain authentication token",
                details={"reason": "token_is_none"},
            )
        return str(token)

    def _build_url(self, path: str) -> str:
        """Build full API URL.

        Args:
            path: API endpoint path

        Returns:
            Full URL for the API endpoint
        """
        # Remove leading slash if present
        path = path.lstrip("/")

        # If path doesn't start with organizations, prepend it
        if not path.startswith("organizations/"):
            path = f"organizations/{self.organization}/{path}"

        return f"{self.base_url}/{path}"

    async def _request(
        self,
        method: str,
        path: str,
        params: Optional[dict[str, Any]] = None,
        json_data: Optional[dict[str, Any]] = None,
        headers: Optional[dict[str, str]] = None,
    ) -> dict[str, Any]:
        """Make an authenticated API request with resilience patterns.

        Args:
            method: HTTP method
            path: API endpoint path
            params: Query parameters
            json_data: JSON request body
            headers: Additional headers

        Returns:
            Response JSON data

        Raises:
            AuthenticationError: If authentication fails
            ExternalServiceError: If API request fails
            AppTimeoutError: If request times out
        """
        if not self.session:
            raise ExternalServiceError(
                service="apigee_client",
                message="Client session not initialized. Use async context manager.",
            )

        # Rate limiting
        if not self.rate_limiter.acquire():
            logger.warning("rate_limit_exceeded", path=path)
            raise ExternalServiceError(
                service="apigee_api",
                message="Rate limit exceeded. Please try again later.",
                status=429,
            )

        url = self._build_url(path)

        # Prepare headers
        request_headers = {
            "Authorization": f"Bearer {self._get_auth_token()}",
            "Content-Type": "application/json",
        }
        if headers:
            request_headers.update(headers)

        logger.info(
            "api_request",
            method=method,
            url=url,
            params=params,
        )

        try:
            # Circuit breaker pattern - returns a coroutine that returns a ClientResponse
            @self.circuit_breaker
            async def make_request_with_circuit_breaker() -> aiohttp.ClientResponse:
                if self.session is None:
                    raise ExternalServiceError(
                        service="apigee_client",
                        message="Client session not initialized",
                    )
                return await self.session.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json_data,
                    headers=request_headers,
                )

            # Execute the request through circuit breaker
            async with await make_request_with_circuit_breaker() as response:
                response_text = await response.text()

                if response.status >= 400:
                    logger.error(
                        "api_error",
                        status=response.status,
                        url=url,
                        response=response_text[:MAX_RESPONSE_LOG_LENGTH],
                    )

                    # Map HTTP status to appropriate exception
                    if response.status == 401:
                        raise AuthenticationError(
                            message="API authentication failed",
                            details={
                                "status": response.status,
                                "url": url,
                            },
                        )
                    elif response.status == 404:
                        from apigee_hybrid_mcp.exceptions import ResourceNotFoundError

                        raise ResourceNotFoundError(
                            resource_type="api_resource",
                            resource_id=path,
                            details={
                                "status": response.status,
                                "response": response_text[:MAX_RESPONSE_DETAIL_LENGTH],
                            },
                        )
                    else:
                        raise ExternalServiceError(
                            service="apigee_api",
                            message=f"API request failed with status {response.status}",
                            status=response.status if response.status >= 500 else 502,
                            details={
                                "status": response.status,
                                "url": url,
                                "response": response_text[:MAX_RESPONSE_DETAIL_LENGTH],
                            },
                        )

                # Parse JSON response
                if response_text:
                    parsed: dict[str, Any] = json.loads(response_text)
                    return parsed
                return {}

        except asyncio.TimeoutError as e:
            logger.error("request_timeout", error=str(e), url=url)
            raise AppTimeoutError(
                operation=f"{method} {path}",
                timeout_seconds=self.settings.request_timeout,
            )
        except aiohttp.ClientError as e:
            logger.error("client_error", error=str(e), url=url)
            raise ExternalServiceError(
                service="apigee_api",
                message=f"Request failed: {str(e)}",
                details={"error_type": type(e).__name__},
            )
        except (
            AuthenticationError,
            ExternalServiceError,
            AppTimeoutError,
        ):
            # Re-raise our custom exceptions
            raise
        except AppError:
            # Re-raise any other AppError subclasses (like ResourceNotFoundError)
            raise
        except Exception as e:
            logger.error("unexpected_error", error=str(e), url=url)
            raise ExternalServiceError(
                service="apigee_api",
                message=f"Unexpected error: {str(e)}",
                details={"error_type": type(e).__name__},
            )

    async def get(self, path: str, params: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        """Make a GET request.

        Args:
            path: API endpoint path
            params: Query parameters

        Returns:
            Response JSON data
        """
        return await self._request("GET", path, params=params)

    async def post(
        self,
        path: str,
        json_data: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Make a POST request.

        Args:
            path: API endpoint path
            json_data: Request body
            params: Query parameters

        Returns:
            Response JSON data
        """
        return await self._request("POST", path, params=params, json_data=json_data)

    async def put(
        self,
        path: str,
        json_data: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Make a PUT request.

        Args:
            path: API endpoint path
            json_data: Request body
            params: Query parameters

        Returns:
            Response JSON data
        """
        return await self._request("PUT", path, params=params, json_data=json_data)

    async def patch(
        self,
        path: str,
        json_data: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Make a PATCH request.

        Args:
            path: API endpoint path
            json_data: Request body
            params: Query parameters

        Returns:
            Response JSON data
        """
        return await self._request("PATCH", path, params=params, json_data=json_data)

    async def delete(self, path: str, params: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        """Make a DELETE request.

        Args:
            path: API endpoint path
            params: Query parameters

        Returns:
            Response JSON data
        """
        return await self._request("DELETE", path, params=params)
