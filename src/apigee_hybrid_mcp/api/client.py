"""Base API client for Apigee Hybrid with authentication and error handling."""
import json
from typing import Any, Optional

import aiohttp
from google.auth.transport.requests import Request
from google.oauth2 import service_account

from apigee_hybrid_mcp.config import Settings
from apigee_hybrid_mcp.utils.logging import get_logger
from apigee_hybrid_mcp.utils.resilience import RateLimiter, create_circuit_breaker

logger = get_logger(__name__)


class ApigeeAPIError(Exception):
    """Base exception for Apigee API errors."""
    
    def __init__(self, message: str, status_code: Optional[int] = None, response_body: Optional[str] = None):
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
            ApigeeAPIError: If credentials are not configured
        """
        if not self.credentials:
            raise ApigeeAPIError("Google Cloud credentials not configured")
            
        if not self.credentials.valid:
            self.credentials.refresh(Request())
            
        return self.credentials.token
        
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
            ApigeeAPIError: If request fails
        """
        if not self.session:
            raise ApigeeAPIError("Client session not initialized. Use async context manager.")
            
        # Rate limiting
        if not self.rate_limiter.acquire():
            logger.warning("rate_limit_exceeded", path=path)
            raise ApigeeAPIError("Rate limit exceeded. Please try again later.")
            
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
            # Circuit breaker pattern
            @self.circuit_breaker
            async def make_request() -> aiohttp.ClientResponse:
                return await self.session.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json_data,
                    headers=request_headers,
                )
                
            response = await make_request()
            response_text = await response.text()
            
            if response.status >= 400:
                logger.error(
                    "api_error",
                    status=response.status,
                    url=url,
                    response=response_text,
                )
                raise ApigeeAPIError(
                    f"API request failed: {response.status}",
                    status_code=response.status,
                    response_body=response_text,
                )
                
            # Parse JSON response
            if response_text:
                return json.loads(response_text)
            return {}
                
        except aiohttp.ClientError as e:
            logger.error("client_error", error=str(e), url=url)
            raise ApigeeAPIError(f"Request failed: {str(e)}")
        except Exception as e:
            logger.error("unexpected_error", error=str(e), url=url)
            raise ApigeeAPIError(f"Unexpected error: {str(e)}")
            
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
