"""Unit tests for Teams functionality.

Tests cover:
- Team model validation
- Repository operations (CRUD)
- Error handling
- Team name uniqueness
- Member validation
"""

import pytest
from datetime import datetime

from apigee_hybrid_mcp.teams.models import Team
from apigee_hybrid_mcp.teams.repository import (
    InMemoryTeamRepository,
    TeamAlreadyExistsError,
    TeamNotFoundError,
)


@pytest.mark.asyncio
class TestTeamModel:
    """Test suite for Team model validation."""

    def test_create_valid_team(self) -> None:
        """Test creating a valid team."""
        team = Team(
            id="team-001",
            name="engineering-team",
            description="Engineering department",
            members=["dev1@example.com", "dev2@example.com"],
        )

        assert team.id == "team-001"
        assert team.name == "engineering-team"
        assert team.description == "Engineering department"
        assert len(team.members) == 2
        assert isinstance(team.created_at, datetime)
        assert isinstance(team.updated_at, datetime)

    def test_team_name_validation_alphanumeric(self) -> None:
        """Test team name accepts alphanumeric with hyphens and underscores."""
        valid_names = ["team-1", "my_team", "TeamName123", "team-name_123"]

        for name in valid_names:
            team = Team(id="test-id", name=name)
            assert team.name == name

    def test_team_name_validation_invalid_chars(self) -> None:
        """Test team name rejects invalid characters."""
        invalid_names = ["team name", "team@name", "team.name", "team/name", "team!name"]

        for name in invalid_names:
            with pytest.raises(ValueError, match="alphanumeric"):
                Team(id="test-id", name=name)

    def test_team_name_validation_empty(self) -> None:
        """Test team name rejects empty or whitespace."""
        # Empty string is caught by Pydantic's min_length
        with pytest.raises(Exception):  # ValidationError or ValueError
            Team(id="test-id", name="")

        # Whitespace strings pass min_length but fail custom validator
        whitespace_names = ["   ", "\t", "\n"]
        for name in whitespace_names:
            with pytest.raises(ValueError, match="cannot be empty"):
                Team(id="test-id", name=name)

    def test_member_email_validation(self) -> None:
        """Test member email validation."""
        # Valid emails
        team = Team(
            id="test-id",
            name="test-team",
            members=["user@example.com", "admin@test.org"],
        )
        assert len(team.members) == 2

        # Invalid email - no @
        with pytest.raises(ValueError, match="Invalid email"):
            Team(
                id="test-id",
                name="test-team",
                members=["invalid-email"],
            )

        # Invalid email - no domain
        with pytest.raises(ValueError, match="Invalid email"):
            Team(
                id="test-id",
                name="test-team",
                members=["user@nodomain"],
            )

    def test_team_defaults(self) -> None:
        """Test default values for optional fields."""
        team = Team(id="test-id", name="test-team")

        assert team.description == ""
        assert team.members == []
        assert isinstance(team.created_at, datetime)
        assert isinstance(team.updated_at, datetime)


@pytest.mark.asyncio
class TestInMemoryTeamRepository:
    """Test suite for InMemoryTeamRepository operations."""

    @pytest.fixture
    def repository(self) -> InMemoryTeamRepository:
        """Provide a fresh repository for each test."""
        return InMemoryTeamRepository()

    async def test_create_team(self, repository: InMemoryTeamRepository) -> None:
        """Test creating a new team."""
        team = await repository.create_team(
            name="engineering",
            description="Engineering team",
            members=["dev1@example.com"],
        )

        assert team.id.startswith("team-")
        assert team.name == "engineering"
        assert team.description == "Engineering team"
        assert len(team.members) == 1

    async def test_create_team_duplicate_name(self, repository: InMemoryTeamRepository) -> None:
        """Test creating a team with duplicate name fails."""
        await repository.create_team(name="engineering")

        with pytest.raises(TeamAlreadyExistsError) as exc_info:
            await repository.create_team(name="engineering")

        assert "engineering" in str(exc_info.value)

    async def test_list_teams_empty(self, repository: InMemoryTeamRepository) -> None:
        """Test listing teams when repository is empty."""
        teams = await repository.list_teams()
        assert teams == []

    async def test_list_teams_multiple(self, repository: InMemoryTeamRepository) -> None:
        """Test listing multiple teams."""
        await repository.create_team(name="team1")
        await repository.create_team(name="team2")
        await repository.create_team(name="team3")

        teams = await repository.list_teams()
        assert len(teams) == 3
        team_names = {team.name for team in teams}
        assert team_names == {"team1", "team2", "team3"}

    async def test_get_team_success(self, repository: InMemoryTeamRepository) -> None:
        """Test getting an existing team."""
        created_team = await repository.create_team(
            name="engineering",
            description="Engineering department",
        )

        retrieved_team = await repository.get_team(created_team.id)

        assert retrieved_team.id == created_team.id
        assert retrieved_team.name == "engineering"
        assert retrieved_team.description == "Engineering department"

    async def test_get_team_not_found(self, repository: InMemoryTeamRepository) -> None:
        """Test getting a non-existent team fails."""
        with pytest.raises(TeamNotFoundError) as exc_info:
            await repository.get_team("non-existent-id")

        assert "non-existent-id" in str(exc_info.value)

    async def test_update_team_description(self, repository: InMemoryTeamRepository) -> None:
        """Test updating team description."""
        team = await repository.create_team(name="engineering", description="Old description")

        updated_team = await repository.update_team(
            team_id=team.id,
            description="New description",
        )

        assert updated_team.id == team.id
        assert updated_team.name == "engineering"
        assert updated_team.description == "New description"
        assert updated_team.updated_at > team.updated_at

    async def test_update_team_members(self, repository: InMemoryTeamRepository) -> None:
        """Test updating team members."""
        team = await repository.create_team(
            name="engineering",
            members=["dev1@example.com"],
        )

        updated_team = await repository.update_team(
            team_id=team.id,
            members=["dev1@example.com", "dev2@example.com", "dev3@example.com"],
        )

        assert len(updated_team.members) == 3
        assert "dev2@example.com" in updated_team.members

    async def test_update_team_name(self, repository: InMemoryTeamRepository) -> None:
        """Test updating team name."""
        team = await repository.create_team(name="old-name")

        updated_team = await repository.update_team(
            team_id=team.id,
            name="new-name",
        )

        assert updated_team.name == "new-name"

        # Verify we can find it by new name
        retrieved = await repository.get_team(team.id)
        assert retrieved.name == "new-name"

    async def test_update_team_name_conflict(self, repository: InMemoryTeamRepository) -> None:
        """Test updating team name to existing name fails."""
        await repository.create_team(name="team1")
        team2 = await repository.create_team(name="team2")

        with pytest.raises(TeamAlreadyExistsError) as exc_info:
            await repository.update_team(team_id=team2.id, name="team1")

        assert "team1" in str(exc_info.value)

    async def test_update_team_not_found(self, repository: InMemoryTeamRepository) -> None:
        """Test updating non-existent team fails."""
        with pytest.raises(TeamNotFoundError):
            await repository.update_team(
                team_id="non-existent-id",
                description="New description",
            )

    async def test_delete_team_success(self, repository: InMemoryTeamRepository) -> None:
        """Test deleting an existing team."""
        team = await repository.create_team(name="engineering")

        await repository.delete_team(team.id)

        # Verify team is deleted
        with pytest.raises(TeamNotFoundError):
            await repository.get_team(team.id)

        # Verify name is available again
        new_team = await repository.create_team(name="engineering")
        assert new_team.id != team.id

    async def test_delete_team_not_found(self, repository: InMemoryTeamRepository) -> None:
        """Test deleting non-existent team fails."""
        with pytest.raises(TeamNotFoundError):
            await repository.delete_team("non-existent-id")

    async def test_concurrent_operations(self, repository: InMemoryTeamRepository) -> None:
        """Test repository handles multiple operations correctly."""
        # Create multiple teams
        await repository.create_team(name="team1", members=["user1@example.com"])
        team2 = await repository.create_team(name="team2", members=["user2@example.com"])
        team3 = await repository.create_team(name="team3", members=["user3@example.com"])

        # Update one
        await repository.update_team(team_id=team2.id, description="Updated team 2")

        # Delete one
        await repository.delete_team(team3.id)

        # List should show 2 teams
        teams = await repository.list_teams()
        assert len(teams) == 2

        team_names = {team.name for team in teams}
        assert team_names == {"team1", "team2"}
