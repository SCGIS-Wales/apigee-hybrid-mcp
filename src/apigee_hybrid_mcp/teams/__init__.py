"""Teams module for Apigee Hybrid MCP.

This module provides team management functionality for Apigee Hybrid,
replacing the deprecated companies API with a modern teams-based approach.
"""

from apigee_hybrid_mcp.teams.models import Team
from apigee_hybrid_mcp.teams.repository import TeamRepository, InMemoryTeamRepository

__all__ = ["Team", "TeamRepository", "InMemoryTeamRepository"]
