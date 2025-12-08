"""Team domain model for Apigee Hybrid.

This module defines the Team entity and related value objects.
Teams represent organizational units that can access APIs, replacing the
deprecated "companies" concept from Apigee OPDK (not applicable in Hybrid).

Note: Apigee Hybrid does not have a native "companies" or "teams" API.
This is a custom implementation for organizational purposes.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class TeamBase(BaseModel):
    """Base model for Team with common fields.
    
    Attributes:
        name: Unique team identifier (immutable after creation)
        description: Human-readable team description
        members: List of member identifiers (email addresses or user IDs)
    """

    name: str = Field(
        ...,
        min_length=3,
        max_length=255,
        pattern=r"^[a-zA-Z0-9\-_]+$",
        description="Team name (alphanumeric, hyphens, underscores only)",
    )
    description: Optional[str] = Field(
        None, max_length=1000, description="Team description"
    )
    members: List[str] = Field(
        default_factory=list,
        description="List of team member identifiers (emails or user IDs)",
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        """Validate team name follows conventions.
        
        Args:
            value: The team name to validate
            
        Returns:
            The validated team name
            
        Raises:
            ValueError: If name is invalid
        """
        if value.startswith("-") or value.endswith("-"):
            raise ValueError("Team name cannot start or end with hyphen")
        if value.startswith("_") or value.endswith("_"):
            raise ValueError("Team name cannot start or end with underscore")
        return value

    @field_validator("members")
    @classmethod
    def validate_members(cls, value: List[str]) -> List[str]:
        """Validate members list.
        
        Args:
            value: List of member identifiers
            
        Returns:
            The validated members list
            
        Raises:
            ValueError: If members list is invalid
        """
        if len(value) != len(set(value)):
            raise ValueError("Duplicate members not allowed")
        return value


class TeamCreate(TeamBase):
    """Model for creating a new team.
    
    Used for POST /teams endpoint.
    """

    pass


class TeamUpdate(BaseModel):
    """Model for updating an existing team.
    
    Used for PUT /teams/{team_id} endpoint.
    All fields are optional for partial updates.
    
    Attributes:
        description: Updated description
        members: Updated members list (replaces existing)
    """

    description: Optional[str] = Field(
        None, max_length=1000, description="Team description"
    )
    members: Optional[List[str]] = Field(
        None, description="List of team member identifiers"
    )

    @field_validator("members")
    @classmethod
    def validate_members(cls, value: Optional[List[str]]) -> Optional[List[str]]:
        """Validate members list.
        
        Args:
            value: List of member identifiers
            
        Returns:
            The validated members list
            
        Raises:
            ValueError: If members list is invalid
        """
        if value is not None and len(value) != len(set(value)):
            raise ValueError("Duplicate members not allowed")
        return value


class Team(TeamBase):
    """Complete Team entity with metadata.
    
    This is the full representation returned by the API.
    
    Attributes:
        id: Unique team identifier (generated server-side)
        name: Team name (inherited from TeamBase)
        description: Team description (inherited from TeamBase)
        members: Team members list (inherited from TeamBase)
        created_at: Timestamp when team was created
        updated_at: Timestamp when team was last updated
    """

    id: str = Field(..., description="Unique team identifier")
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="Creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, description="Last update timestamp"
    )

    model_config = {"from_attributes": True}

    def to_dict(self) -> Dict[str, Any]:
        """Convert team to dictionary representation.
        
        Returns:
            Dictionary representation of the team
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "members": self.members,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
