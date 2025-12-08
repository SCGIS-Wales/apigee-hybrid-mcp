"""Unit tests for Teams API functionality.

Tests cover:
- Listing teams
- Getting team details
- Creating teams
- Updating teams
- Deleting teams
- Validation logic
- Error handling
"""

import pytest
from datetime import datetime

from apigee_hybrid_mcp.models.team import Team, TeamCreate, TeamUpdate
from apigee_hybrid_mcp.repository.team_repository import (
    InMemoryTeamRepository,
    TeamAlreadyExistsError,
    TeamNotFoundError,
)


class TestTeamModel:
    """Test suite for Team domain model."""

    def test_team_create_valid(self) -> None:
        """Test creating a valid team."""
        team_data = TeamCreate(
            name="engineering-team",
            description="Engineering department team",
            members=["user1@example.com", "user2@example.com"],
        )
        assert team_data.name == "engineering-team"
        assert team_data.description == "Engineering department team"
        assert len(team_data.members) == 2

    def test_team_create_minimal(self) -> None:
        """Test creating a team with minimal data."""
        team_data = TeamCreate(name="minimal-team")
        assert team_data.name == "minimal-team"
        assert team_data.description is None
        assert team_data.members == []

    def test_team_name_validation_invalid_pattern(self) -> None:
        """Test team name validation rejects invalid patterns."""
        with pytest.raises(ValueError, match="String should match pattern"):
            TeamCreate(name="invalid team!")

    def test_team_name_validation_too_short(self) -> None:
        """Test team name validation rejects names that are too short."""
        with pytest.raises(ValueError, match="at least 3 characters"):
            TeamCreate(name="ab")

    def test_team_name_validation_hyphen_edges(self) -> None:
        """Test team name validation rejects hyphens at edges."""
        with pytest.raises(ValueError, match="cannot start or end with hyphen"):
            TeamCreate(name="-invalid")
        with pytest.raises(ValueError, match="cannot start or end with hyphen"):
            TeamCreate(name="invalid-")

    def test_team_name_validation_underscore_edges(self) -> None:
        """Test team name validation rejects underscores at edges."""
        with pytest.raises(ValueError, match="cannot start or end with underscore"):
            TeamCreate(name="_invalid")
        with pytest.raises(ValueError, match="cannot start or end with underscore"):
            TeamCreate(name="invalid_")

    def test_team_members_validation_duplicates(self) -> None:
        """Test team members validation rejects duplicates."""
        with pytest.raises(ValueError, match="Duplicate members not allowed"):
            TeamCreate(
                name="test-team",
                members=["user1@example.com", "user1@example.com"],
            )

    def test_team_update_partial(self) -> None:
        """Test partial team update."""
        update_data = TeamUpdate(description="Updated description")
        assert update_data.description == "Updated description"
        assert update_data.members is None

    def test_team_to_dict(self) -> None:
        """Test converting team to dictionary."""
        team = Team(
            id="team-123",
            name="test-team",
            description="Test team",
            members=["user1@example.com"],
            created_at=datetime(2024, 1, 1, 0, 0, 0),
            updated_at=datetime(2024, 1, 2, 0, 0, 0),
        )
        team_dict = team.to_dict()
        assert team_dict["id"] == "team-123"
        assert team_dict["name"] == "test-team"
        assert team_dict["description"] == "Test team"
        assert team_dict["members"] == ["user1@example.com"]
        assert "created_at" in team_dict
        assert "updated_at" in team_dict


@pytest.mark.asyncio
class TestInMemoryTeamRepository:
    """Test suite for InMemoryTeamRepository."""

    async def test_create_team_success(self) -> None:
        """Test creating a team successfully."""
        repo = InMemoryTeamRepository()
        team_data = TeamCreate(
            name="engineering",
            description="Engineering team",
            members=["dev1@example.com", "dev2@example.com"],
        )

        team = await repo.create(team_data)

        assert team.id is not None
        assert team.name == "engineering"
        assert team.description == "Engineering team"
        assert len(team.members) == 2
        assert team.created_at is not None
        assert team.updated_at is not None

    async def test_create_team_duplicate_name(self) -> None:
        """Test creating a team with duplicate name raises error."""
        repo = InMemoryTeamRepository()
        team_data = TeamCreate(name="engineering")

        await repo.create(team_data)

        with pytest.raises(TeamAlreadyExistsError, match="engineering"):
            await repo.create(team_data)

    async def test_get_by_id_success(self) -> None:
        """Test getting a team by ID successfully."""
        repo = InMemoryTeamRepository()
        team_data = TeamCreate(name="engineering")
        created_team = await repo.create(team_data)

        retrieved_team = await repo.get_by_id(created_team.id)

        assert retrieved_team is not None
        assert retrieved_team.id == created_team.id
        assert retrieved_team.name == created_team.name

    async def test_get_by_id_not_found(self) -> None:
        """Test getting a non-existent team by ID returns None."""
        repo = InMemoryTeamRepository()

        team = await repo.get_by_id("non-existent-id")

        assert team is None

    async def test_get_by_name_success(self) -> None:
        """Test getting a team by name successfully."""
        repo = InMemoryTeamRepository()
        team_data = TeamCreate(name="engineering")
        await repo.create(team_data)

        team = await repo.get_by_name("engineering")

        assert team is not None
        assert team.name == "engineering"

    async def test_get_by_name_not_found(self) -> None:
        """Test getting a non-existent team by name returns None."""
        repo = InMemoryTeamRepository()

        team = await repo.get_by_name("non-existent")

        assert team is None

    async def test_list_all_empty(self) -> None:
        """Test listing all teams when repository is empty."""
        repo = InMemoryTeamRepository()

        teams = await repo.list_all()

        assert len(teams) == 0

    async def test_list_all_multiple_teams(self) -> None:
        """Test listing all teams with multiple teams."""
        repo = InMemoryTeamRepository()
        await repo.create(TeamCreate(name="team1"))
        await repo.create(TeamCreate(name="team2"))
        await repo.create(TeamCreate(name="team3"))

        teams = await repo.list_all()

        assert len(teams) == 3
        team_names = [t.name for t in teams]
        assert "team1" in team_names
        assert "team2" in team_names
        assert "team3" in team_names

    async def test_update_team_success(self) -> None:
        """Test updating a team successfully."""
        repo = InMemoryTeamRepository()
        team_data = TeamCreate(name="engineering", description="Old description")
        created_team = await repo.create(team_data)

        update_data = TeamUpdate(
            description="New description",
            members=["new1@example.com", "new2@example.com"],
        )
        updated_team = await repo.update(created_team.id, update_data)

        assert updated_team.id == created_team.id
        assert updated_team.name == created_team.name
        assert updated_team.description == "New description"
        assert len(updated_team.members) == 2
        assert updated_team.updated_at > created_team.updated_at

    async def test_update_team_partial(self) -> None:
        """Test partial update of a team."""
        repo = InMemoryTeamRepository()
        team_data = TeamCreate(
            name="engineering",
            description="Old description",
            members=["old@example.com"],
        )
        created_team = await repo.create(team_data)

        update_data = TeamUpdate(description="New description")
        updated_team = await repo.update(created_team.id, update_data)

        assert updated_team.description == "New description"
        assert updated_team.members == ["old@example.com"]

    async def test_update_team_not_found(self) -> None:
        """Test updating a non-existent team raises error."""
        repo = InMemoryTeamRepository()
        update_data = TeamUpdate(description="New description")

        with pytest.raises(TeamNotFoundError, match="non-existent-id"):
            await repo.update("non-existent-id", update_data)

    async def test_delete_team_success(self) -> None:
        """Test deleting a team successfully."""
        repo = InMemoryTeamRepository()
        team_data = TeamCreate(name="engineering")
        created_team = await repo.create(team_data)

        deleted = await repo.delete(created_team.id)

        assert deleted is True
        retrieved_team = await repo.get_by_id(created_team.id)
        assert retrieved_team is None

    async def test_delete_team_not_found(self) -> None:
        """Test deleting a non-existent team returns False."""
        repo = InMemoryTeamRepository()

        deleted = await repo.delete("non-existent-id")

        assert deleted is False

    async def test_exists_by_name_true(self) -> None:
        """Test exists_by_name returns True for existing team."""
        repo = InMemoryTeamRepository()
        await repo.create(TeamCreate(name="engineering"))

        exists = await repo.exists_by_name("engineering")

        assert exists is True

    async def test_exists_by_name_false(self) -> None:
        """Test exists_by_name returns False for non-existent team."""
        repo = InMemoryTeamRepository()

        exists = await repo.exists_by_name("non-existent")

        assert exists is False

    async def test_team_immutability(self) -> None:
        """Test that team name cannot be changed after creation."""
        repo = InMemoryTeamRepository()
        team_data = TeamCreate(name="engineering")
        created_team = await repo.create(team_data)

        update_data = TeamUpdate(description="New description")
        updated_team = await repo.update(created_team.id, update_data)

        # Name should remain unchanged
        assert updated_team.name == created_team.name
