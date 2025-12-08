"""Configuration management for Apigee Hybrid MCP Server.

This module provides functional configuration management using Pydantic settings.
All configuration is immutable and loaded from environment variables or .env file.

Environment Variables:
    APIGEE_MCP_GOOGLE_PROJECT_ID: Google Cloud Project ID
    APIGEE_MCP_GOOGLE_CREDENTIALS_PATH: Path to service account JSON
    APIGEE_MCP_APIGEE_ORGANIZATION: Apigee organization name
    APIGEE_MCP_LOG_LEVEL: Logging level (DEBUG, INFO, WARNING, ERROR)
    APIGEE_MCP_MAX_RETRIES: Maximum retry attempts for failed requests
    APIGEE_MCP_REQUEST_TIMEOUT: Request timeout in seconds

Example:
    from apigee_hybrid_mcp.config import get_settings
    
    settings = get_settings()
    print(f"Organization: {settings.apigee_organization}")
"""
import os
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support.
    
    This class uses Pydantic for type-safe configuration management.
    All settings can be overridden via environment variables with
    the APIGEE_MCP_ prefix.
    """

    # Google Cloud Configuration
    google_project_id: str = Field(
        default="",
        description="Google Cloud Project ID for API authentication",
    )
    google_credentials_path: Optional[str] = Field(
        default=None,
        description="Path to Google Cloud service account credentials JSON file",
    )
    
    # Apigee Configuration
    apigee_organization: str = Field(
        default="",
        description="Apigee organization name (required for all API calls)",
    )
    apigee_api_base_url: str = Field(
        default="https://apigee.googleapis.com/v1",
        description="Apigee API base URL (default: v1 REST API)",
    )
    
    # Server Configuration
    server_host: str = Field(
        default="0.0.0.0",
        description="MCP server host address",
    )
    server_port: int = Field(
        default=8080,
        description="MCP server port number",
    )
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
    )
    
    # Resilience Configuration
    max_retries: int = Field(
        default=3,
        description="Maximum number of retries for failed API requests",
    )
    retry_backoff_factor: float = Field(
        default=2.0,
        description="Exponential backoff multiplier for retries",
    )
    request_timeout: int = Field(
        default=30,
        description="HTTP request timeout in seconds",
    )
    circuit_breaker_failure_threshold: int = Field(
        default=5,
        description="Number of failures before circuit breaker opens",
    )
    circuit_breaker_timeout: int = Field(
        default=60,
        description="Circuit breaker timeout in seconds before retry",
    )
    
    # Rate Limiting
    rate_limit_requests: int = Field(
        default=100,
        description="Maximum requests allowed per rate limit window",
    )
    rate_limit_window: int = Field(
        default=60,
        description="Rate limit window duration in seconds",
    )

    class Config:
        """Pydantic configuration."""
        env_prefix = "APIGEE_MCP_"
        case_sensitive = False
        env_file = ".env"
        env_file_encoding = "utf-8"


def get_settings() -> Settings:
    """Get application settings instance.
    
    This function creates and returns a configured Settings object.
    Settings are loaded from environment variables and .env file.
    
    Returns:
        Settings: Configured settings instance with all parameters
        
    Example:
        >>> settings = get_settings()
        >>> print(settings.apigee_organization)
        'my-org'
    """
    return Settings()
