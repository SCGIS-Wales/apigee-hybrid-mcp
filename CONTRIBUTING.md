# Contributing to Apigee Hybrid MCP Server

Thank you for your interest in contributing to Apigee Hybrid MCP Server! This document provides guidelines and instructions for contributing.

## Code of Conduct

This project adheres to a code of conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to info@scgis.wales.

## How to Contribute

### Reporting Bugs

Before creating bug reports, please check existing issues. When creating a bug report, include:

- Clear and descriptive title
- Exact steps to reproduce the problem
- Expected behavior
- Actual behavior
- Environment details (OS, Python version - should be 3.14+, etc.)
- Relevant logs or error messages

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. Include:

- Clear and descriptive title
- Detailed description of the enhancement
- Use case and benefits
- Possible implementation approach

### Pull Requests

1. **Fork the repository** and create your branch from `main`
2. **Make your changes**:
   - Follow the coding style (see below)
   - Add tests for new functionality
   - Update documentation as needed
3. **Test your changes**:
   ```bash
   # Run tests
   pytest
   
   # Run linting
   black src/ tests/
   ruff check src/ tests/
   mypy src/
   
   # Run security checks
   bandit -r src/
   safety check
   ```
4. **Commit your changes** with clear commit messages
5. **Push to your fork** and submit a pull request

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting, etc.)
- `refactor:` Code refactoring
- `test:` Adding or updating tests
- `chore:` Maintenance tasks

Examples:
```
feat: add support for Analytics API
fix: handle connection timeout in API client
docs: update deployment guide for EKS
```

## Development Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/SCGIS-Wales/apigee-hybrid-mcp.git
   cd apigee-hybrid-mcp
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements-dev.txt
   pip install -e .
   ```

4. **Set up pre-commit hooks** (optional):
   ```bash
   pip install pre-commit
   pre-commit install
   ```

## Coding Style

### Python Style

- Follow [PEP 8](https://pep8.org/)
- Use [Black](https://black.readthedocs.io/) for formatting (line length: 100)
- Use [Ruff](https://docs.astral.sh/ruff/) for linting
- Use type hints for all function signatures
- Write docstrings for all public modules, classes, and functions

### Functional Programming

- Prefer pure functions without side effects
- Use immutable data structures
- Avoid classes when functions suffice
- Make dependencies explicit (pass as parameters)
- Handle errors explicitly

### Example

```python
"""Module for handling API operations.

This module provides functional utilities for interacting with the Apigee API.
All functions are pure and have no side effects.
"""

from typing import Dict, Any


def build_api_url(base_url: str, organization: str, path: str) -> str:
    """Build a complete API URL from components.
    
    This is a pure function that constructs URLs without side effects.
    
    Args:
        base_url: Base URL for the API
        organization: Organization identifier
        path: API endpoint path
        
    Returns:
        str: Complete URL for the API endpoint
        
    Example:
        >>> build_api_url("https://api.example.com", "org1", "apis")
        'https://api.example.com/organizations/org1/apis'
    """
    path = path.lstrip("/")
    return f"{base_url}/organizations/{organization}/{path}"
```

## Testing

### Writing Tests

- Write tests for all new functionality
- Use pytest fixtures for setup
- Mock external dependencies
- Aim for >80% code coverage
- Test both success and failure cases

### Test Structure

```python
"""Unit tests for API operations."""

import pytest
from unittest.mock import AsyncMock

@pytest.mark.asyncio
class TestAPIOperations:
    """Test suite for API operations."""
    
    async def test_successful_request(self, mock_client):
        """Test successful API request."""
        # Arrange
        expected_response = {"status": "success"}
        mock_client.get.return_value = expected_response
        
        # Act
        result = await mock_client.get("test-path")
        
        # Assert
        assert result == expected_response
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/apigee_hybrid_mcp --cov-report=html

# Run specific test file
pytest tests/unit/test_api_products.py

# Run with verbose output
pytest -v
```

## Documentation

- Update README.md for user-facing changes
- Update inline documentation (docstrings)
- Add examples for new features
- Update CHANGELOG.md

## Release Process

1. Update VERSION file with new version (semver)
2. Update CHANGELOG.md with changes
3. Create pull request to `main`
4. After merge, create and push a git tag:
   ```bash
   git tag -a v1.1.0 -m "Release version 1.1.0"
   git push origin v1.1.0
   ```
5. GitHub Actions will automatically:
   - Run tests
   - Build and publish Docker images
   - Create GitHub release
   - Publish Helm chart

## Questions?

Feel free to ask questions by:
- Opening a GitHub issue
- Emailing info@scgis.wales

Thank you for contributing!
