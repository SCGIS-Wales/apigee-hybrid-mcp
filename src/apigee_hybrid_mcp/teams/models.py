"""Team data models for Apigee Hybrid MCP.

This module defines the Team model with validation using Pydantic.
Teams represent groups of developers or organizations that share API access.
"""

from datetime import UTC, datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Team(BaseModel):
    """Team model for organizing API consumers.

    Teams provide a way to manage API access for groups of developers,
    replacing the deprecated companies concept in Apigee OPDK.

    Attributes:
        id: Unique team identifier (immutable after creation)
        name: Team name (must be unique within organization)
        description: Optional team description
        members: List of member email addresses
        created_at: Timestamp of team creation
        updated_at: Timestamp of last update

    Example:
        >>> team = Team(
        ...     id="team-001",
        ...     name="engineering-team",
        ...     description="Engineering department API access",
        ...     members=["dev1@example.com", "dev2@example.com"]
        ... )
    """

    id: str = Field(..., description="Unique team identifier", min_length=1, max_length=255)
    name: str = Field(..., description="Team name", min_length=1, max_length=255)
    description: Optional[str] = Field(default="", description="Team description")
    members: List[str] = Field(default_factory=list, description="List of member emails")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Last update timestamp"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "team-engineering",
                "name": "engineering-team",
                "description": "Engineering department API access",
                "members": ["dev1@example.com", "dev2@example.com"],
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
            }
        }
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        """Validate team name format.

        Args:
            value: Team name to validate

        Returns:
            str: Validated team name

        Raises:
            ValueError: If name contains invalid characters
        """
        if not value or not value.strip():
            raise ValueError("Team name cannot be empty or whitespace")

        # Allow alphanumeric, hyphens, underscores
        allowed_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_")
        if not all(c in allowed_chars for c in value):
            raise ValueError(
                "Team name can only contain alphanumeric characters, hyphens, and underscores"
            )

        return value

    @field_validator("members")
    @classmethod
    def validate_members(cls, value: List[str]) -> List[str]:
        """Validate member email addresses.

        Args:
            value: List of member email addresses

        Returns:
            List[str]: Validated member list

        Raises:
            ValueError: If any email is invalid
        """
        for email in value:
            if "@" not in email or "." not in email:
                raise ValueError(f"Invalid email address: {email}")

        return value
