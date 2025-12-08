"""Team repository interfaces and implementations.

This module defines the repository interface for Team entities
and provides an in-memory implementation for development/testing.
Production implementations could use Cloud Datastore, Firestore, etc.
"""

import uuid
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from apigee_hybrid_mcp.models.team import Team, TeamCreate, TeamUpdate


class TeamNotFoundError(Exception):
    """Exception raised when a team is not found."""

    def __init__(self, team_id: str):
        """Initialize exception.

        Args:
            team_id: ID of the team that was not found
        """
        self.team_id = team_id
        super().__init__(f"Team not found: {team_id}")


class TeamAlreadyExistsError(Exception):
    """Exception raised when attempting to create a team that already exists."""

    def __init__(self, team_name: str):
        """Initialize exception.

        Args:
            team_name: Name of the team that already exists
        """
        self.team_name = team_name
        super().__init__(f"Team already exists: {team_name}")


class TeamRepository(ABC):
    """Abstract base class for Team repositories.

    This interface defines the contract for team data persistence.
    Implementations can use different storage backends (in-memory,
    Cloud Datastore, Firestore, PostgreSQL, etc.).
    """

    @abstractmethod
    async def create(self, team_data: TeamCreate) -> Team:
        """Create a new team.

        Args:
            team_data: Team creation data

        Returns:
            Created team with generated ID and timestamps

        Raises:
            TeamAlreadyExistsError: If team with same name exists
        """
        pass

    @abstractmethod
    async def get_by_id(self, team_id: str) -> Optional[Team]:
        """Get team by ID.

        Args:
            team_id: Team identifier

        Returns:
            Team if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[Team]:
        """Get team by name.

        Args:
            name: Team name

        Returns:
            Team if found, None otherwise
        """
        pass

    @abstractmethod
    async def list_all(self) -> List[Team]:
        """List all teams.

        Returns:
            List of all teams
        """
        pass

    @abstractmethod
    async def update(self, team_id: str, team_data: TeamUpdate) -> Team:
        """Update an existing team.

        Args:
            team_id: Team identifier
            team_data: Team update data

        Returns:
            Updated team

        Raises:
            TeamNotFoundError: If team not found
        """
        pass

    @abstractmethod
    async def delete(self, team_id: str) -> bool:
        """Delete a team.

        Args:
            team_id: Team identifier

        Returns:
            True if deleted, False if not found
        """
        pass

    @abstractmethod
    async def exists_by_name(self, name: str) -> bool:
        """Check if a team with given name exists.

        Args:
            name: Team name

        Returns:
            True if exists, False otherwise
        """
        pass


class InMemoryTeamRepository(TeamRepository):
    """In-memory implementation of TeamRepository.

    This implementation stores teams in memory and is suitable for:
    - Development and testing
    - Single-instance deployments
    - Prototyping

    For production with multiple instances, use a persistent storage
    backend like Cloud Datastore or Firestore.

    Attributes:
        _teams: Dictionary mapping team IDs to Team objects
        _teams_by_name: Dictionary mapping team names to team IDs (for quick lookup)
    """

    def __init__(self) -> None:
        """Initialize the repository with empty storage."""
        self._teams: Dict[str, Team] = {}
        self._teams_by_name: Dict[str, str] = {}

    async def create(self, team_data: TeamCreate) -> Team:
        """Create a new team.

        Args:
            team_data: Team creation data

        Returns:
            Created team with generated ID and timestamps

        Raises:
            TeamAlreadyExistsError: If team with same name exists
        """
        # Check for duplicate name
        if await self.exists_by_name(team_data.name):
            raise TeamAlreadyExistsError(team_data.name)

        # Generate ID and timestamps
        team_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)

        # Create team entity
        team = Team(
            id=team_id,
            name=team_data.name,
            description=team_data.description,
            members=team_data.members.copy(),
            created_at=now,
            updated_at=now,
        )

        # Store team
        self._teams[team_id] = team
        self._teams_by_name[team_data.name] = team_id

        return team

    async def get_by_id(self, team_id: str) -> Optional[Team]:
        """Get team by ID.

        Args:
            team_id: Team identifier

        Returns:
            Team if found, None otherwise
        """
        return self._teams.get(team_id)

    async def get_by_name(self, name: str) -> Optional[Team]:
        """Get team by name.

        Args:
            name: Team name

        Returns:
            Team if found, None otherwise
        """
        team_id = self._teams_by_name.get(name)
        if team_id:
            return self._teams.get(team_id)
        return None

    async def list_all(self) -> List[Team]:
        """List all teams.

        Returns:
            List of all teams sorted by creation date
        """
        teams = list(self._teams.values())
        teams.sort(key=lambda t: t.created_at)
        return teams

    async def update(self, team_id: str, team_data: TeamUpdate) -> Team:
        """Update an existing team.

        Args:
            team_id: Team identifier
            team_data: Team update data

        Returns:
            Updated team

        Raises:
            TeamNotFoundError: If team not found
        """
        team = await self.get_by_id(team_id)
        if not team:
            raise TeamNotFoundError(team_id)

        # Update fields
        updated_fields: Dict[str, Any] = {}
        if team_data.description is not None:
            updated_fields["description"] = team_data.description
        if team_data.members is not None:
            updated_fields["members"] = team_data.members.copy()

        # Set update timestamp
        updated_fields["updated_at"] = datetime.now(timezone.utc)

        # Create updated team (immutable pattern)
        updated_team = team.model_copy(update=updated_fields)
        self._teams[team_id] = updated_team

        return updated_team

    async def delete(self, team_id: str) -> bool:
        """Delete a team.

        Args:
            team_id: Team identifier

        Returns:
            True if deleted, False if not found
        """
        team = await self.get_by_id(team_id)
        if not team:
            return False

        # Remove from both indices
        del self._teams[team_id]
        del self._teams_by_name[team.name]

        return True

    async def exists_by_name(self, name: str) -> bool:
        """Check if a team with given name exists.

        Args:
            name: Team name

        Returns:
            True if exists, False otherwise
        """
        return name in self._teams_by_name
