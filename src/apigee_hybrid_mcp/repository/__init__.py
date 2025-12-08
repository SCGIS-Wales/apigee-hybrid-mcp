"""Repository layer for data persistence.

This module provides an abstraction layer for data storage,
following the Repository pattern from DDD.
"""

from apigee_hybrid_mcp.repository.team_repository import (
    InMemoryTeamRepository,
    TeamRepository,
)

__all__ = ["TeamRepository", "InMemoryTeamRepository"]
