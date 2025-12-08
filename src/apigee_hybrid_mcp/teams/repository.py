"""Repository pattern implementation for Teams.

This module provides an abstraction layer for team persistence,
allowing easy swapping between in-memory and datastore implementations.
"""

from abc import ABC, abstractmethod
from datetime import UTC, datetime
from typing import Dict, List, Optional
from uuid import uuid4

from apigee_hybrid_mcp.teams.models import Team


class TeamNotFoundError(Exception):
    """Exception raised when a team is not found."""

    def __init__(self, team_id: str) -> None:
        """Initialize exception.

        Args:
            team_id: ID of the team that was not found
        """
        self.team_id = team_id
        super().__init__(f"Team not found: {team_id}")


class TeamAlreadyExistsError(Exception):
    """Exception raised when attempting to create a team that already exists."""

    def __init__(self, name: str) -> None:
        """Initialize exception.

        Args:
            name: Name of the team that already exists
        """
        self.name = name
        super().__init__(f"Team already exists with name: {name}")


class TeamRepository(ABC):
    """Abstract base class for team repositories.

    This interface defines the contract for team persistence,
    enabling different storage backends (in-memory, database, etc.).
    """

    @abstractmethod
    async def list_teams(self) -> List[Team]:
        """List all teams.

        Returns:
            List[Team]: All teams in the repository
        """
        pass

    @abstractmethod
    async def get_team(self, team_id: str) -> Team:
        """Get a team by ID.

        Args:
            team_id: Team identifier

        Returns:
            Team: The requested team

        Raises:
            TeamNotFoundError: If team does not exist
        """
        pass

    @abstractmethod
    async def create_team(
        self, name: str, description: str = "", members: Optional[List[str]] = None
    ) -> Team:
        """Create a new team.

        Args:
            name: Team name (must be unique)
            description: Optional team description
            members: Optional list of member emails

        Returns:
            Team: The created team

        Raises:
            TeamAlreadyExistsError: If team with name already exists
        """
        pass

    @abstractmethod
    async def update_team(
        self,
        team_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        members: Optional[List[str]] = None,
    ) -> Team:
        """Update an existing team.

        Args:
            team_id: Team identifier
            name: New team name (must be unique if changed)
            description: New team description
            members: New list of member emails

        Returns:
            Team: The updated team

        Raises:
            TeamNotFoundError: If team does not exist
            TeamAlreadyExistsError: If new name conflicts with existing team
        """
        pass

    @abstractmethod
    async def delete_team(self, team_id: str) -> None:
        """Delete a team.

        Args:
            team_id: Team identifier

        Raises:
            TeamNotFoundError: If team does not exist
        """
        pass


class InMemoryTeamRepository(TeamRepository):
    """In-memory implementation of TeamRepository.

    This implementation stores teams in memory using a dictionary.
    Suitable for development and testing, not for production use.
    """

    def __init__(self) -> None:
        """Initialize the in-memory repository."""
        self._teams: Dict[str, Team] = {}
        self._name_index: Dict[str, str] = {}  # name -> team_id mapping

    async def list_teams(self) -> List[Team]:
        """List all teams.

        Returns:
            List[Team]: All teams in the repository
        """
        return list(self._teams.values())

    async def get_team(self, team_id: str) -> Team:
        """Get a team by ID.

        Args:
            team_id: Team identifier

        Returns:
            Team: The requested team

        Raises:
            TeamNotFoundError: If team does not exist
        """
        if team_id not in self._teams:
            raise TeamNotFoundError(team_id)

        return self._teams[team_id]

    async def create_team(
        self, name: str, description: str = "", members: Optional[List[str]] = None
    ) -> Team:
        """Create a new team.

        Args:
            name: Team name (must be unique)
            description: Optional team description
            members: Optional list of member emails

        Returns:
            Team: The created team

        Raises:
            TeamAlreadyExistsError: If team with name already exists
        """
        # Check for name uniqueness
        if name in self._name_index:
            raise TeamAlreadyExistsError(name)

        # Generate unique ID
        team_id = f"team-{uuid4().hex[:12]}"

        # Create team
        team = Team(
            id=team_id,
            name=name,
            description=description,
            members=members or [],
        )

        # Store team
        self._teams[team_id] = team
        self._name_index[name] = team_id

        return team

    async def update_team(
        self,
        team_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        members: Optional[List[str]] = None,
    ) -> Team:
        """Update an existing team.

        Args:
            team_id: Team identifier
            name: New team name (must be unique if changed)
            description: New team description
            members: New list of member emails

        Returns:
            Team: The updated team

        Raises:
            TeamNotFoundError: If team does not exist
            TeamAlreadyExistsError: If new name conflicts with existing team
        """
        if team_id not in self._teams:
            raise TeamNotFoundError(team_id)

        team = self._teams[team_id]

        # Check name uniqueness if changing name
        if name is not None and name != team.name:
            if name in self._name_index:
                raise TeamAlreadyExistsError(name)

            # Update name index
            del self._name_index[team.name]
            self._name_index[name] = team_id

        # Create updated team
        updated_team = Team(
            id=team.id,
            name=name if name is not None else team.name,
            description=description if description is not None else team.description,
            members=members if members is not None else team.members,
            created_at=team.created_at,
            updated_at=datetime.now(UTC),
        )

        self._teams[team_id] = updated_team

        return updated_team

    async def delete_team(self, team_id: str) -> None:
        """Delete a team.

        Args:
            team_id: Team identifier

        Raises:
            TeamNotFoundError: If team does not exist
        """
        if team_id not in self._teams:
            raise TeamNotFoundError(team_id)

        team = self._teams[team_id]
        del self._teams[team_id]
        del self._name_index[team.name]
