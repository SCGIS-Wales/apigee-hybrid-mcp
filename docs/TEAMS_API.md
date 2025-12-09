# Teams API Documentation

## Overview

The Teams API provides organizational team management capabilities for Apigee Hybrid. This is a **custom implementation** specifically designed for Apigee Hybrid environments, as Apigee Hybrid does not provide a native teams or companies API (unlike Apigee OPDK).

## Quick Start

```bash
# List all teams
list-teams

# Create a team
create-team --name engineering-team --description "Engineering department"

# Get team details
get-team --team_id <team-id>

# Update team
update-team --team_id <team-id> --description "Updated description"

# Delete team
delete-team --team_id <team-id>
```

## API Reference

See inline documentation in the code for detailed API specifications.

## Architecture

The Teams API follows Domain-Driven Design (DDD) principles with separate domain, repository, and presentation layers.

For complete documentation, see the inline docstrings in:
- `src/apigee_hybrid_mcp/models/team.py`
- `src/apigee_hybrid_mcp/repository/team_repository.py`
- `tests/unit/test_teams.py`
