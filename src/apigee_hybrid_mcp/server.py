"""Functional MCP server implementation for Apigee Hybrid.

This module implements the Model Context Protocol (MCP) server for Apigee Hybrid
API management. It provides tools for interacting with all Apigee APIs using
functional programming patterns.

Architecture:
    - Functional design with pure functions where possible
    - Immutable data structures
    - Explicit error handling
    - Comprehensive inline documentation
    - Type hints for all functions

Main Components:
    - Tool registration and handling
    - API client management
    - Request/response transformation
    - Error handling and logging

Example Usage:
    from apigee_hybrid_mcp.server import main

    if __name__ == "__main__":
        main()
"""

import asyncio
import json
from typing import Any, Dict, List

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from apigee_hybrid_mcp.api.client import ApigeeClient
from apigee_hybrid_mcp.config import get_settings
from apigee_hybrid_mcp.repository.team_repository import (
    InMemoryTeamRepository,
)
from apigee_hybrid_mcp.utils.logging import configure_logging, get_logger
from apigee_hybrid_mcp.validation import ParameterValidator

# Initialize logger
logger = get_logger(__name__)

# Initialize MCP server
app = Server("apigee-hybrid-mcp")

# Initialize team repository (singleton for this server instance)
team_repository = InMemoryTeamRepository()


def create_tool_definition(
    name: str,
    description: str,
    parameters: Dict[str, Any],
) -> Tool:
    """Create an MCP tool definition.

    This is a pure function that constructs a Tool object with the given
    parameters. It follows MCP specifications for tool definitions.

    Args:
        name: Unique tool identifier (kebab-case recommended)
        description: Human-readable description of what the tool does
        parameters: JSON Schema object defining the tool's parameters

    Returns:
        Tool: MCP tool definition object

    Example:
        >>> tool = create_tool_definition(
        ...     name="list-organizations",
        ...     description="Lists all Apigee organizations",
        ...     parameters={"type": "object", "properties": {}}
        ... )
    """
    return Tool(
        name=name,
        description=description,
        inputSchema=parameters,
    )


def format_api_response(
    data: Dict[str, Any],
    operation: str,
) -> List[TextContent]:
    """Format API response data for MCP text content.

    Transforms API response dictionaries into MCP-compatible text content.
    Uses JSON formatting for readability.

    Args:
        data: API response data dictionary
        operation: Description of the operation performed

    Returns:
        List[TextContent]: Formatted response for MCP client

    Example:
        >>> response = {"name": "org-1", "displayName": "Organization 1"}
        >>> content = format_api_response(response, "Get Organization")
        >>> print(content[0].text)
        Operation: Get Organization
        {
          "name": "org-1",
          "displayName": "Organization 1"
        }
    """
    formatted_json = json.dumps(data, indent=2)
    text = f"Operation: {operation}\n\n{formatted_json}"
    return [TextContent(type="text", text=text)]


def handle_api_error(error: Exception, operation: str) -> List[TextContent]:
    """Handle API errors and format error messages.

    Provides consistent error handling and formatting across all tools.
    Uses the new exception handling system for structured errors.

    Args:
        error: The exception that occurred
        operation: Description of the failed operation

    Returns:
        List[TextContent]: Formatted error message for MCP client

    Example:
        >>> try:
        ...     # API call
        ...     pass
        ... except Exception as e:
        ...     return handle_api_error(e, "List Organizations")
    """
    # Use new error formatter with proper logging and correlation IDs
    return format_error_response(error, operation, include_traceback=False)


@app.list_tools()
async def list_tools() -> List[Tool]:
    """List all available MCP tools for Apigee Hybrid.

    This handler returns the complete list of tools exposed by the MCP server.
    Each tool corresponds to one or more Apigee API operations.

    Returns:
        List[Tool]: All available tools with their definitions

    Tool Categories:
        - Organizations: Manage Apigee organizations
        - Environments: Manage deployment environments
        - API Proxies: Manage API proxy lifecycle
        - Developers: Manage API consumers
        - Apps: Manage developer and company applications
        - API Products: Manage API product bundles
        - Shared Flows: Manage reusable policy flows
        - Keystores: Manage certificates and keys
        - Teams: Manage teams for organizational access
        - Debug Sessions: Trace and debug API requests
    """
    return [
        # Organizations API
        create_tool_definition(
            name="list-organizations",
            description="List all Apigee organizations accessible by the authenticated user",
            parameters={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
        create_tool_definition(
            name="get-organization",
            description="Get details of a specific Apigee organization",
            parameters={
                "type": "object",
                "properties": {
                    "organization": {
                        "type": "string",
                        "description": "Organization ID or name",
                    },
                },
                "required": ["organization"],
            },
        ),
        # Environments API
        create_tool_definition(
            name="list-environments",
            description="List all environments in an Apigee organization",
            parameters={
                "type": "object",
                "properties": {
                    "organization": {
                        "type": "string",
                        "description": "Organization ID",
                    },
                },
                "required": ["organization"],
            },
        ),
        create_tool_definition(
            name="get-environment",
            description="Get details of a specific environment",
            parameters={
                "type": "object",
                "properties": {
                    "organization": {
                        "type": "string",
                        "description": "Organization ID",
                    },
                    "environment": {
                        "type": "string",
                        "description": "Environment name",
                    },
                },
                "required": ["organization", "environment"],
            },
        ),
        create_tool_definition(
            name="create-environment",
            description="Create a new environment in an organization",
            parameters={
                "type": "object",
                "properties": {
                    "organization": {
                        "type": "string",
                        "description": "Organization ID",
                    },
                    "name": {
                        "type": "string",
                        "description": "Environment name",
                    },
                    "displayName": {
                        "type": "string",
                        "description": "Display name for the environment",
                    },
                    "description": {
                        "type": "string",
                        "description": "Environment description",
                    },
                    "type": {
                        "type": "string",
                        "enum": ["PRODUCTION", "NON_PRODUCTION"],
                        "description": "Environment type",
                    },
                },
                "required": ["organization", "name"],
            },
        ),
        # API Proxies API
        create_tool_definition(
            name="list-api-proxies",
            description="List all API proxies in an organization",
            parameters={
                "type": "object",
                "properties": {
                    "organization": {
                        "type": "string",
                        "description": "Organization ID",
                    },
                    "includeRevisions": {
                        "type": "boolean",
                        "description": "Include revision details",
                    },
                },
                "required": ["organization"],
            },
        ),
        create_tool_definition(
            name="get-api-proxy",
            description="Get details of a specific API proxy including all revisions",
            parameters={
                "type": "object",
                "properties": {
                    "organization": {
                        "type": "string",
                        "description": "Organization ID",
                    },
                    "proxy": {
                        "type": "string",
                        "description": "API proxy name",
                    },
                },
                "required": ["organization", "proxy"],
            },
        ),
        create_tool_definition(
            name="get-api-proxy-revision",
            description="Get details of a specific API proxy revision",
            parameters={
                "type": "object",
                "properties": {
                    "organization": {
                        "type": "string",
                        "description": "Organization ID",
                    },
                    "proxy": {
                        "type": "string",
                        "description": "API proxy name",
                    },
                    "revision": {
                        "type": "string",
                        "description": "Revision number",
                    },
                },
                "required": ["organization", "proxy", "revision"],
            },
        ),
        create_tool_definition(
            name="deploy-api-proxy",
            description="Deploy an API proxy revision to an environment",
            parameters={
                "type": "object",
                "properties": {
                    "organization": {
                        "type": "string",
                        "description": "Organization ID",
                    },
                    "environment": {
                        "type": "string",
                        "description": "Environment name",
                    },
                    "proxy": {
                        "type": "string",
                        "description": "API proxy name",
                    },
                    "revision": {
                        "type": "string",
                        "description": "Revision number to deploy",
                    },
                    "override": {
                        "type": "boolean",
                        "description": "Override existing deployment",
                    },
                },
                "required": ["organization", "environment", "proxy", "revision"],
            },
        ),
        create_tool_definition(
            name="undeploy-api-proxy",
            description="Undeploy an API proxy revision from an environment",
            parameters={
                "type": "object",
                "properties": {
                    "organization": {
                        "type": "string",
                        "description": "Organization ID",
                    },
                    "environment": {
                        "type": "string",
                        "description": "Environment name",
                    },
                    "proxy": {
                        "type": "string",
                        "description": "API proxy name",
                    },
                    "revision": {
                        "type": "string",
                        "description": "Revision number to undeploy",
                    },
                },
                "required": ["organization", "environment", "proxy", "revision"],
            },
        ),
        # Developers API
        create_tool_definition(
            name="list-developers",
            description="List all developers in an organization",
            parameters={
                "type": "object",
                "properties": {
                    "organization": {
                        "type": "string",
                        "description": "Organization ID",
                    },
                    "expand": {
                        "type": "boolean",
                        "description": "Include detailed information",
                    },
                },
                "required": ["organization"],
            },
        ),
        create_tool_definition(
            name="get-developer",
            description="Get details of a specific developer",
            parameters={
                "type": "object",
                "properties": {
                    "organization": {
                        "type": "string",
                        "description": "Organization ID",
                    },
                    "developer": {
                        "type": "string",
                        "description": "Developer email or ID",
                    },
                },
                "required": ["organization", "developer"],
            },
        ),
        create_tool_definition(
            name="create-developer",
            description="Create a new developer in an organization",
            parameters={
                "type": "object",
                "properties": {
                    "organization": {
                        "type": "string",
                        "description": "Organization ID",
                    },
                    "email": {
                        "type": "string",
                        "description": "Developer email (required, unique)",
                    },
                    "firstName": {
                        "type": "string",
                        "description": "First name",
                    },
                    "lastName": {
                        "type": "string",
                        "description": "Last name",
                    },
                    "userName": {
                        "type": "string",
                        "description": "Username",
                    },
                },
                "required": ["organization", "email", "firstName", "lastName"],
            },
        ),
        # Developer Apps API
        create_tool_definition(
            name="list-developer-apps",
            description="List all apps for a specific developer",
            parameters={
                "type": "object",
                "properties": {
                    "organization": {
                        "type": "string",
                        "description": "Organization ID",
                    },
                    "developer": {
                        "type": "string",
                        "description": "Developer email or ID",
                    },
                    "expand": {
                        "type": "boolean",
                        "description": "Include app details",
                    },
                },
                "required": ["organization", "developer"],
            },
        ),
        create_tool_definition(
            name="get-developer-app",
            description="Get details of a developer app including credentials",
            parameters={
                "type": "object",
                "properties": {
                    "organization": {
                        "type": "string",
                        "description": "Organization ID",
                    },
                    "developer": {
                        "type": "string",
                        "description": "Developer email or ID",
                    },
                    "app": {
                        "type": "string",
                        "description": "App name",
                    },
                },
                "required": ["organization", "developer", "app"],
            },
        ),
        create_tool_definition(
            name="create-developer-app",
            description="Create a new developer app with API product associations",
            parameters={
                "type": "object",
                "properties": {
                    "organization": {
                        "type": "string",
                        "description": "Organization ID",
                    },
                    "developer": {
                        "type": "string",
                        "description": "Developer email or ID",
                    },
                    "name": {
                        "type": "string",
                        "description": "App name",
                    },
                    "apiProducts": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of API product names",
                    },
                    "callbackUrl": {
                        "type": "string",
                        "description": "OAuth callback URL",
                    },
                },
                "required": ["organization", "developer", "name"],
            },
        ),
        # API Products API
        create_tool_definition(
            name="list-api-products",
            description="List all API products in an organization",
            parameters={
                "type": "object",
                "properties": {
                    "organization": {
                        "type": "string",
                        "description": "Organization ID",
                    },
                    "expand": {
                        "type": "boolean",
                        "description": "Include detailed information",
                    },
                },
                "required": ["organization"],
            },
        ),
        create_tool_definition(
            name="get-api-product",
            description="Get details of a specific API product",
            parameters={
                "type": "object",
                "properties": {
                    "organization": {
                        "type": "string",
                        "description": "Organization ID",
                    },
                    "product": {
                        "type": "string",
                        "description": "API product name",
                    },
                },
                "required": ["organization", "product"],
            },
        ),
        create_tool_definition(
            name="create-api-product",
            description="Create a new API product with quotas and rate limits",
            parameters={
                "type": "object",
                "properties": {
                    "organization": {
                        "type": "string",
                        "description": "Organization ID",
                    },
                    "name": {
                        "type": "string",
                        "description": "Product name (required, immutable)",
                    },
                    "displayName": {
                        "type": "string",
                        "description": "Display name",
                    },
                    "description": {
                        "type": "string",
                        "description": "Product description",
                    },
                    "approvalType": {
                        "type": "string",
                        "enum": ["auto", "manual"],
                        "description": "Approval type for apps",
                    },
                    "proxies": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of API proxy names",
                    },
                    "environments": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of environment names",
                    },
                    "quota": {
                        "type": "string",
                        "description": "Quota limit",
                    },
                    "quotaInterval": {
                        "type": "string",
                        "description": "Quota interval",
                    },
                    "quotaTimeUnit": {
                        "type": "string",
                        "enum": ["minute", "hour", "day", "month"],
                        "description": "Quota time unit",
                    },
                },
                "required": ["organization", "name"],
            },
        ),
        # Shared Flows API
        create_tool_definition(
            name="list-shared-flows",
            description="List all shared flows in an organization",
            parameters={
                "type": "object",
                "properties": {
                    "organization": {
                        "type": "string",
                        "description": "Organization ID",
                    },
                    "includeRevisions": {
                        "type": "boolean",
                        "description": "Include revision details",
                    },
                },
                "required": ["organization"],
            },
        ),
        create_tool_definition(
            name="get-shared-flow",
            description="Get details of a specific shared flow",
            parameters={
                "type": "object",
                "properties": {
                    "organization": {
                        "type": "string",
                        "description": "Organization ID",
                    },
                    "sharedFlow": {
                        "type": "string",
                        "description": "Shared flow name",
                    },
                },
                "required": ["organization", "sharedFlow"],
            },
        ),
        create_tool_definition(
            name="deploy-shared-flow",
            description="Deploy a shared flow revision to an environment",
            parameters={
                "type": "object",
                "properties": {
                    "organization": {
                        "type": "string",
                        "description": "Organization ID",
                    },
                    "environment": {
                        "type": "string",
                        "description": "Environment name",
                    },
                    "sharedFlow": {
                        "type": "string",
                        "description": "Shared flow name",
                    },
                    "revision": {
                        "type": "string",
                        "description": "Revision number to deploy",
                    },
                },
                "required": ["organization", "environment", "sharedFlow", "revision"],
            },
        ),
        # Keystores API
        create_tool_definition(
            name="list-keystores",
            description="List all keystores in an environment",
            parameters={
                "type": "object",
                "properties": {
                    "organization": {
                        "type": "string",
                        "description": "Organization ID",
                    },
                    "environment": {
                        "type": "string",
                        "description": "Environment name",
                    },
                },
                "required": ["organization", "environment"],
            },
        ),
        create_tool_definition(
            name="get-keystore",
            description="Get details of a specific keystore including aliases",
            parameters={
                "type": "object",
                "properties": {
                    "organization": {
                        "type": "string",
                        "description": "Organization ID",
                    },
                    "environment": {
                        "type": "string",
                        "description": "Environment name",
                    },
                    "keystore": {
                        "type": "string",
                        "description": "Keystore name",
                    },
                },
                "required": ["organization", "environment", "keystore"],
            },
        ),
        create_tool_definition(
            name="list-keystore-aliases",
            description="List all aliases (certificates) in a keystore",
            parameters={
                "type": "object",
                "properties": {
                    "organization": {
                        "type": "string",
                        "description": "Organization ID",
                    },
                    "environment": {
                        "type": "string",
                        "description": "Environment name",
                    },
                    "keystore": {
                        "type": "string",
                        "description": "Keystore name",
                    },
                },
                "required": ["organization", "environment", "keystore"],
            },
        ),
        create_tool_definition(
            name="get-keystore-alias",
            description="Get details of a specific keystore alias (certificate)",
            parameters={
                "type": "object",
                "properties": {
                    "organization": {
                        "type": "string",
                        "description": "Organization ID",
                    },
                    "environment": {
                        "type": "string",
                        "description": "Environment name",
                    },
                    "keystore": {
                        "type": "string",
                        "description": "Keystore name",
                    },
                    "alias": {
                        "type": "string",
                        "description": "Alias name",
                    },
                },
                "required": ["organization", "environment", "keystore", "alias"],
            },
        ),
        # Companies (Teams) API
        create_tool_definition(
            name="list-teams",
            description="List all teams",
            parameters={
                "type": "object",
                "properties": {},
            },
        ),
        create_tool_definition(
            name="get-team",
            description="Get details of a specific team",
            parameters={
                "type": "object",
                "properties": {
                    "team_id": {
                        "type": "string",
                        "description": "Team ID",
                    },
                },
                "required": ["team_id"],
            },
        ),
        create_tool_definition(
            name="create-team",
            description="Create a new team",
            parameters={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Team name (unique, alphanumeric with hyphens/underscores)",
                    },
                    "description": {
                        "type": "string",
                        "description": "Team description",
                    },
                    "members": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of team member identifiers (emails or user IDs)",
                    },
                },
                "required": ["name"],
            },
        ),
        create_tool_definition(
            name="update-team",
            description="Update an existing team",
            parameters={
                "type": "object",
                "properties": {
                    "team_id": {
                        "type": "string",
                        "description": "Team ID",
                    },
                    "description": {
                        "type": "string",
                        "description": "Updated team description",
                    },
                    "members": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Updated list of team members",
                    },
                },
                "required": ["team_id"],
            },
        ),
        create_tool_definition(
            name="delete-team",
            description="Delete a team",
            parameters={
                "type": "object",
                "properties": {
                    "team_id": {
                        "type": "string",
                        "description": "Team ID",
                    },
                },
                "required": ["team_id"],
            },
        ),
        # Debug Sessions (Trace) API
        create_tool_definition(
            name="create-debug-session",
            description="Create a debug session (trace) for an API proxy",
            parameters={
                "type": "object",
                "properties": {
                    "organization": {
                        "type": "string",
                        "description": "Organization ID",
                    },
                    "environment": {
                        "type": "string",
                        "description": "Environment name",
                    },
                    "proxy": {
                        "type": "string",
                        "description": "API proxy name",
                    },
                    "revision": {
                        "type": "string",
                        "description": "Revision number",
                    },
                    "session": {
                        "type": "string",
                        "description": "Session ID (UUID recommended)",
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Session timeout in seconds (max 600)",
                    },
                },
                "required": ["organization", "environment", "proxy", "revision", "session"],
            },
        ),
        create_tool_definition(
            name="get-debug-session-data",
            description="Get captured transaction data from a debug session",
            parameters={
                "type": "object",
                "properties": {
                    "organization": {
                        "type": "string",
                        "description": "Organization ID",
                    },
                    "environment": {
                        "type": "string",
                        "description": "Environment name",
                    },
                    "proxy": {
                        "type": "string",
                        "description": "API proxy name",
                    },
                    "revision": {
                        "type": "string",
                        "description": "Revision number",
                    },
                    "session": {
                        "type": "string",
                        "description": "Session ID",
                    },
                },
                "required": ["organization", "environment", "proxy", "revision", "session"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle MCP tool calls and route to appropriate Apigee API operations.

    This is the main tool call handler that routes requests to the appropriate
    API functions based on the tool name. It manages the API client lifecycle
    and error handling.

    Args:
        name: Tool name (as defined in list_tools)
        arguments: Tool arguments dictionary (validated against input schema)

    Returns:
        List[TextContent]: Formatted API response or error message

    Raises:
        ValueError: If tool name is not recognized

    Implementation Notes:
        - Uses async context manager for API client lifecycle
        - All errors are caught and formatted consistently
        - Logging is performed for all operations
        - API client handles retries and circuit breaking
    """
    settings = get_settings()

    try:
        async with ApigeeClient(settings) as client:
            # Organizations API
            if name == "get-organization":
                org = arguments.get("organization", settings.apigee_organization)
                data = await client.get(f"organizations/{org}")
                return format_api_response(data, "Get Organization")

            # Environments API
            elif name == "list-environments":
                org = arguments.get("organization", settings.apigee_organization)
                data = await client.get("environments")
                return format_api_response(data, "List Environments")

            elif name == "get-environment":
                org = arguments.get("organization", settings.apigee_organization)
                env = arguments["environment"]
                data = await client.get(f"environments/{env}")
                return format_api_response(data, f"Get Environment: {env}")

            elif name == "create-environment":
                org = arguments.get("organization", settings.apigee_organization)
                env_data = {
                    "name": arguments["name"],
                    "displayName": arguments.get("displayName", arguments["name"]),
                    "description": arguments.get("description", ""),
                    "type": arguments.get("type", "NON_PRODUCTION"),
                }
                data = await client.post("environments", json_data=env_data)
                return format_api_response(data, "Create Environment")

            # API Proxies API
            elif name == "list-api-proxies":
                org = arguments.get("organization", settings.apigee_organization)
                params = {}
                if arguments.get("includeRevisions"):
                    params["includeRevisions"] = "true"
                data = await client.get("apis", params=params)
                return format_api_response(data, "List API Proxies")

            elif name == "get-api-proxy":
                org = arguments.get("organization", settings.apigee_organization)
                proxy = arguments["proxy"]
                data = await client.get(f"apis/{proxy}")
                return format_api_response(data, f"Get API Proxy: {proxy}")

            elif name == "get-api-proxy-revision":
                org = arguments.get("organization", settings.apigee_organization)
                proxy = arguments["proxy"]
                revision = arguments["revision"]
                data = await client.get(f"apis/{proxy}/revisions/{revision}")
                return format_api_response(
                    data, f"Get API Proxy Revision: {proxy} (rev {revision})"
                )

            elif name == "deploy-api-proxy":
                org = arguments.get("organization", settings.apigee_organization)
                env = arguments["environment"]
                proxy = arguments["proxy"]
                revision = arguments["revision"]
                params = {}
                if arguments.get("override"):
                    params["override"] = "true"
                data = await client.post(
                    f"environments/{env}/apis/{proxy}/revisions/{revision}/deployments",
                    params=params,
                )
                return format_api_response(
                    data, f"Deploy API Proxy: {proxy} rev {revision} to {env}"
                )

            elif name == "undeploy-api-proxy":
                org = arguments.get("organization", settings.apigee_organization)
                env = arguments["environment"]
                proxy = arguments["proxy"]
                revision = arguments["revision"]
                data = await client.delete(
                    f"environments/{env}/apis/{proxy}/revisions/{revision}/deployments"
                )
                return format_api_response(
                    data, f"Undeploy API Proxy: {proxy} rev {revision} from {env}"
                )

            # Developers API
            elif name == "list-developers":
                org = arguments.get("organization", settings.apigee_organization)
                params = {}
                if arguments.get("expand"):
                    params["expand"] = "true"
                data = await client.get("developers", params=params)
                return format_api_response(data, "List Developers")

            elif name == "get-developer":
                org = arguments.get("organization", settings.apigee_organization)
                developer = arguments["developer"]
                data = await client.get(f"developers/{developer}")
                return format_api_response(data, f"Get Developer: {developer}")

            elif name == "create-developer":
                org = arguments.get("organization", settings.apigee_organization)
                dev_data = {
                    "email": arguments["email"],
                    "firstName": arguments["firstName"],
                    "lastName": arguments["lastName"],
                    "userName": arguments.get("userName", arguments["email"].split("@")[0]),
                }
                data = await client.post("developers", json_data=dev_data)
                return format_api_response(data, "Create Developer")

            # Developer Apps API
            elif name == "list-developer-apps":
                org = arguments.get("organization", settings.apigee_organization)
                developer = arguments["developer"]
                params = {}
                if arguments.get("expand"):
                    params["expand"] = "true"
                data = await client.get(f"developers/{developer}/apps", params=params)
                return format_api_response(data, f"List Developer Apps: {developer}")

            elif name == "get-developer-app":
                org = arguments.get("organization", settings.apigee_organization)
                developer = arguments["developer"]
                app = arguments["app"]
                data = await client.get(f"developers/{developer}/apps/{app}")
                return format_api_response(data, f"Get Developer App: {app}")

            elif name == "create-developer-app":
                org = arguments.get("organization", settings.apigee_organization)
                developer = arguments["developer"]
                app_data = {
                    "name": arguments["name"],
                    "apiProducts": arguments.get("apiProducts", []),
                }
                if "callbackUrl" in arguments:
                    app_data["callbackUrl"] = arguments["callbackUrl"]
                data = await client.post(f"developers/{developer}/apps", json_data=app_data)
                return format_api_response(data, "Create Developer App")

            # API Products API
            elif name == "list-api-products":
                org = arguments.get("organization", settings.apigee_organization)
                params = {}
                if arguments.get("expand"):
                    params["expand"] = "true"
                data = await client.get("apiproducts", params=params)
                return format_api_response(data, "List API Products")

            elif name == "get-api-product":
                org = arguments.get("organization", settings.apigee_organization)
                product = arguments["product"]
                data = await client.get(f"apiproducts/{product}")
                return format_api_response(data, f"Get API Product: {product}")

            elif name == "create-api-product":
                org = arguments.get("organization", settings.apigee_organization)
                product_data = {
                    "name": arguments["name"],
                    "displayName": arguments.get("displayName", arguments["name"]),
                    "description": arguments.get("description", ""),
                    "approvalType": arguments.get("approvalType", "auto"),
                    "proxies": arguments.get("proxies", []),
                    "environments": arguments.get("environments", []),
                    "apiResources": ["/**"],
                }
                if "quota" in arguments:
                    product_data["quota"] = arguments["quota"]
                    product_data["quotaInterval"] = arguments.get("quotaInterval", "1")
                    product_data["quotaTimeUnit"] = arguments.get("quotaTimeUnit", "day")
                data = await client.post("apiproducts", json_data=product_data)
                return format_api_response(data, "Create API Product")

            # Shared Flows API
            elif name == "list-shared-flows":
                org = arguments.get("organization", settings.apigee_organization)
                params = {}
                if arguments.get("includeRevisions"):
                    params["includeRevisions"] = "true"
                data = await client.get("sharedflows", params=params)
                return format_api_response(data, "List Shared Flows")

            elif name == "get-shared-flow":
                org = arguments.get("organization", settings.apigee_organization)
                sharedflow = arguments["sharedFlow"]
                data = await client.get(f"sharedflows/{sharedflow}")
                return format_api_response(data, f"Get Shared Flow: {sharedflow}")

            elif name == "deploy-shared-flow":
                org = arguments.get("organization", settings.apigee_organization)
                env = arguments["environment"]
                sharedflow = arguments["sharedFlow"]
                revision = arguments["revision"]
                data = await client.post(
                    f"environments/{env}/sharedflows/{sharedflow}/revisions/{revision}/deployments"
                )
                return format_api_response(
                    data, f"Deploy Shared Flow: {sharedflow} rev {revision} to {env}"
                )

            # Keystores API
            elif name == "list-keystores":
                org = arguments.get("organization", settings.apigee_organization)
                env = arguments["environment"]
                data = await client.get(f"environments/{env}/keystores")
                return format_api_response(data, f"List Keystores in {env}")

            elif name == "get-keystore":
                org = arguments.get("organization", settings.apigee_organization)
                env = arguments["environment"]
                keystore = arguments["keystore"]
                data = await client.get(f"environments/{env}/keystores/{keystore}")
                return format_api_response(data, f"Get Keystore: {keystore}")

            elif name == "list-keystore-aliases":
                org = arguments.get("organization", settings.apigee_organization)
                env = arguments["environment"]
                keystore = arguments["keystore"]
                data = await client.get(f"environments/{env}/keystores/{keystore}/aliases")
                return format_api_response(data, f"List Keystore Aliases: {keystore}")

            elif name == "get-keystore-alias":
                org = arguments.get("organization", settings.apigee_organization)
                env = arguments["environment"]
                keystore = arguments["keystore"]
                alias = arguments["alias"]
                data = await client.get(f"environments/{env}/keystores/{keystore}/aliases/{alias}")
                return format_api_response(data, f"Get Keystore Alias: {alias}")

            # Companies (Teams) API
            elif name == "list-companies":
                org = arguments.get("organization", settings.apigee_organization)
                params = {}
                if arguments.get("expand"):
                    params["expand"] = "true"
                data = await client.get("companies", params=params)
                return format_api_response(data, "List Companies")

            elif name == "get-company":
                org = arguments.get("organization", settings.apigee_organization)
                company = arguments["company"]
                data = await client.get(f"companies/{company}")
                return format_api_response(data, f"Get Company: {company}")

            elif name == "create-company":
                org = arguments.get("organization", settings.apigee_organization)
                company_data = {
                    "name": arguments["name"],
                    "displayName": arguments.get("displayName", arguments["name"]),
                }
                data = await client.post("companies", json_data=company_data)
                return format_api_response(data, "Create Company")

            # Teams API (custom implementation for Apigee Hybrid)
            elif name == "list-teams":
                try:
                    teams = await team_repository.list_all()
                    teams_data = [team.to_dict() for team in teams]
                    return format_api_response({"teams": teams_data}, "List Teams")
                except Exception as e:
                    mapped_error = map_repository_error(e)
                    return handle_api_error(mapped_error, name)

            elif name == "get-team":
                try:
                    team_id = ParameterValidator.validate_non_empty_string(
                        arguments.get("team_id"), "team_id"
                    )
                    team = await team_repository.get_by_id(team_id)
                    if not team:
                        from apigee_hybrid_mcp.exceptions import ResourceNotFoundError

                        raise ResourceNotFoundError(
                            resource_type="team",
                            resource_id=team_id,
                        )
                    return format_api_response(team.to_dict(), f"Get Team: {team_id}")
                except (AppError, TeamNotFoundError) as e:
                    mapped_error = map_repository_error(e)
                    return handle_api_error(mapped_error, name)

            elif name == "create-team":
                try:
                    # Validate required parameters
                    name_val = ParameterValidator.validate_non_empty_string(
                        arguments.get("name"), "name"
                    )

                    # Create team data with validation via Pydantic
                    team_data = TeamCreate(
                        name=name_val,
                        description=arguments.get("description"),
                        members=arguments.get("members", []),
                    )

                    team = await team_repository.create(team_data)
                    logger.info(
                        "team_created",
                        team_id=team.id,
                        team_name=team.name,
                    )
                    return format_api_response(team.to_dict(), "Create Team")
                except (AppError, TeamAlreadyExistsError) as e:
                    mapped_error = map_repository_error(e)
                    return handle_api_error(mapped_error, name)
                except ValueError as e:
                    # Pydantic validation errors
                    return handle_api_error(
                        InvalidParameterError(
                            parameter="team_data",
                            value="",
                            reason=str(e),
                        ),
                        name,
                    )

            elif name == "update-team":
                try:
                    team_id = ParameterValidator.validate_non_empty_string(
                        arguments.get("team_id"), "team_id"
                    )

                    # Create update data
                    update_data = TeamUpdate(
                        description=arguments.get("description"),
                        members=arguments.get("members"),
                    )

                    team = await team_repository.update(team_id, update_data)
                    logger.info(
                        "team_updated",
                        team_id=team.id,
                        team_name=team.name,
                    )
                    return format_api_response(team.to_dict(), f"Update Team: {team_id}")
                except (AppError, TeamNotFoundError) as e:
                    mapped_error = map_repository_error(e)
                    return handle_api_error(mapped_error, name)
                except ValueError as e:
                    return handle_api_error(
                        InvalidParameterError(
                            parameter="team_data",
                            value="",
                            reason=str(e),
                        ),
                        name,
                    )

            elif name == "delete-team":
                try:
                    team_id = ParameterValidator.validate_non_empty_string(
                        arguments.get("team_id"), "team_id"
                    )
                    await team_repository.delete(team_id)
                    logger.info("team_deleted", team_id=team_id)
                    return format_api_response(
                        {"success": True, "team_id": team_id},
                        f"Delete Team: {team_id}",
                    )
                except (AppError, TeamNotFoundError) as e:
                    mapped_error = map_repository_error(e)
                    return handle_api_error(mapped_error, name)

            # Debug Sessions (Trace) API
            elif name == "create-debug-session":
                org = arguments.get("organization", settings.apigee_organization)
                env = arguments["environment"]
                proxy = arguments["proxy"]
                revision = arguments["revision"]
                session = arguments["session"]
                params = {"session": session}
                if "timeout" in arguments:
                    params["timeout"] = str(arguments["timeout"])
                data = await client.post(
                    f"environments/{env}/apis/{proxy}/revisions/{revision}/debugsessions",
                    params=params,
                )
                return format_api_response(data, f"Create Debug Session: {session}")

            elif name == "get-debug-session-data":
                org = arguments.get("organization", settings.apigee_organization)
                env = arguments["environment"]
                proxy = arguments["proxy"]
                revision = arguments["revision"]
                session = arguments["session"]
                data = await client.get(
                    f"environments/{env}/apis/{proxy}/revisions/{revision}/debugsessions/{session}/data"
                )
                return format_api_response(data, f"Get Debug Session Data: {session}")

            else:
                raise ValueError(f"Unknown tool: {name}")

    except Exception as e:
        return handle_api_error(e, name)


def main() -> None:
    """Initialize and start the Apigee Hybrid MCP server.

    Initializes logging, configures the server, and starts the MCP
    stdio server for communication with MCP clients.

    This function:
        1. Loads configuration from environment
        2. Configures structured logging
        3. Starts the MCP server via stdio transport
        4. Handles graceful shutdown

    Example:
        Run from command line:
        $ python -m apigee_hybrid_mcp.server

        Or programmatically:
        >>> from apigee_hybrid_mcp.server import main
        >>> main()
    """
    settings = get_settings()
    configure_logging(settings.log_level)

    logger.info(
        "starting_mcp_server",
        organization=settings.apigee_organization,
        api_base_url=settings.apigee_api_base_url,
    )

    async def run_server() -> None:
        """Async server runner."""
        async with stdio_server() as (read_stream, write_stream):
            await app.run(
                read_stream,
                write_stream,
                app.create_initialization_options(),
            )

    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        logger.info("server_stopped", reason="keyboard_interrupt")
    except Exception as e:
        logger.error("server_error", error=str(e))
        raise


if __name__ == "__main__":
    main()
