# Apigee Hybrid MCP Server

A highly resilient and scalable Model Context Protocol (MCP) server for Google Apigee Hybrid API management, built with functional Python programming principles.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.14+](https://img.shields.io/badge/python-3.14+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-ready-brightgreen.svg)](https://www.docker.com/)
[![Kubernetes](https://img.shields.io/badge/kubernetes-ready-326CE5.svg)](https://kubernetes.io/)

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
  - [Local Development](#local-development)
  - [Docker](#docker)
  - [AWS ECS](#aws-ecs-deployment)
  - [AWS EKS with Helm](#aws-eks-deployment-with-helm)
- [MCP Integration](#mcp-integration)
  - [VS Code](#vs-code-integration)
  - [Claude Desktop](#claude-desktop-integration)
- [API Coverage](#api-coverage)
- [Testing](#testing)
- [Security](#security)
- [Monitoring](#monitoring)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## 🎯 Overview

This MCP server provides a comprehensive interface to Google Apigee Hybrid APIs, enabling seamless interaction with all Apigee resources through the Model Context Protocol. Built with enterprise-grade reliability patterns including circuit breakers, retries, and rate limiting.

### Key Highlights

- **Functional Python Design**: Pure functions, immutable data structures, explicit error handling
- **Comprehensive API Coverage**: All major Apigee Hybrid APIs (Organizations, Environments, API Proxies, Developers, Apps, API Products, Shared Flows, Keystores, Companies, Debug Sessions)
- **Production-Ready**: Circuit breakers, exponential backoff, rate limiting, structured logging
- **Containerized**: Multi-stage Docker builds with security best practices
- **Cloud-Native**: Ready for AWS ECS and EKS deployment with Helm charts
- **Well-Documented**: Inline documentation, comprehensive README, archived API docs

## ✨ Features

### MCP Server Capabilities

- ✅ **Organizations Management**: List, get, and update organizations
- ✅ **Environments**: Create, configure, and manage deployment environments
- ✅ **API Proxy Lifecycle**: Deploy, undeploy, list, and manage API proxy revisions
- ✅ **Developer Management**: Create, update, and manage API consumers
- ✅ **App Management**: Developer apps with credential management
- ✅ **API Products**: Define product bundles with quotas and rate limits
- ✅ **Shared Flows**: Reusable policy sequences
- ✅ **Keystores & Truststores**: Certificate and key management with aliases
- ✅ **Teams**: Modern team-based API access management (replaces deprecated Companies API)
- ✅ **Debug Sessions (Trace)**: Request tracing and troubleshooting

### Technical Features

- 🔒 **Security**: Non-root container, read-only filesystem, dropped capabilities
- 🔄 **Resilience**: Circuit breakers, retry logic with exponential backoff
- 📊 **Observability**: Structured logging (JSON), comprehensive error handling
- ⚡ **Performance**: Rate limiting, connection pooling, async I/O
- 🧪 **Testing**: Comprehensive unit tests with pytest, test coverage reporting
- 🔍 **Code Quality**: Static analysis (ruff, mypy, black), type hints

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│         MCP Client (VS Code / Claude)           │
└────────────────┬────────────────────────────────┘
                 │ stdio / HTTP
                 ▼
┌─────────────────────────────────────────────────┐
│          Apigee Hybrid MCP Server               │
│  ┌──────────────────────────────────────────┐   │
│  │  MCP Protocol Handler                    │   │
│  │  - Tool Registration                     │   │
│  │  - Request Routing                       │   │
│  │  - Response Formatting                   │   │
│  └──────────────┬───────────────────────────┘   │
│                 ▼                                │
│  ┌──────────────────────────────────────────┐   │
│  │  Resilience Layer                        │   │
│  │  - Circuit Breaker                       │   │
│  │  - Retry Logic                           │   │
│  │  - Rate Limiter                          │   │
│  └──────────────┬───────────────────────────┘   │
│                 ▼                                │
│  ┌──────────────────────────────────────────┐   │
│  │  Apigee API Client                       │   │
│  │  - Authentication (OAuth2)               │   │
│  │  - Request Builder                       │   │
│  │  - Response Parser                       │   │
│  └──────────────┬───────────────────────────┘   │
└─────────────────┼────────────────────────────────┘
                  │ HTTPS
                  ▼
┌─────────────────────────────────────────────────┐
│     Google Apigee Hybrid API (REST v1)          │
└─────────────────────────────────────────────────┘
```

## 📦 Prerequisites

### Required

- Python 3.14+
- Google Cloud Project with Apigee organization
- Service Account with Apigee API permissions
- Docker (for containerized deployment)

### Optional

- AWS CLI (for ECS/EKS deployment)
- kubectl & helm (for Kubernetes deployment)
- VS Code or Claude Desktop (for MCP client integration)

## 🚀 Installation

### Local Installation

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
   pip install -r requirements.txt
   ```

4. **Install in development mode**:
   ```bash
   pip install -e .
   ```

### Docker Installation

1. **Build the image**:
   ```bash
   docker build -t apigee-hybrid-mcp:latest .
   ```

2. **Run with Docker Compose**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   docker-compose up -d
   ```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```bash
# Google Cloud Configuration
GOOGLE_PROJECT_ID=your-project-id
APIGEE_ORGANIZATION=your-org-name
GOOGLE_CREDENTIALS_PATH=./credentials/service-account.json

# Server Configuration
LOG_LEVEL=INFO
SERVER_HOST=0.0.0.0
SERVER_PORT=8080

# Resilience Configuration
MAX_RETRIES=3
RETRY_BACKOFF_FACTOR=2.0
REQUEST_TIMEOUT=30
CIRCUIT_BREAKER_FAILURE_THRESHOLD=5
CIRCUIT_BREAKER_TIMEOUT=60

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60
```

### Service Account Setup

1. **Create service account**:
   ```bash
   gcloud iam service-accounts create apigee-mcp-sa \
     --display-name="Apigee MCP Server"
   ```

2. **Grant permissions**:
   ```bash
   gcloud projects add-iam-policy-binding PROJECT_ID \
     --member="serviceAccount:apigee-mcp-sa@PROJECT_ID.iam.gserviceaccount.com" \
     --role="roles/apigee.admin"
   ```

3. **Create key**:
   ```bash
   gcloud iam service-accounts keys create credentials/service-account.json \
     --iam-account=apigee-mcp-sa@PROJECT_ID.iam.gserviceaccount.com
   ```

## 💻 Usage

### Local Development

Run the MCP server locally:

```bash
# Set environment variables
export APIGEE_MCP_GOOGLE_PROJECT_ID=your-project-id
export APIGEE_MCP_APIGEE_ORGANIZATION=your-org-name
export APIGEE_MCP_GOOGLE_CREDENTIALS_PATH=./credentials/service-account.json

# Run the server
python -m apigee_hybrid_mcp.server
```

### Docker

Using Docker Compose:

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

Using Docker directly:

```bash
docker run -d \
  --name apigee-mcp \
  -v $(pwd)/credentials:/app/credentials:ro \
  -e APIGEE_MCP_GOOGLE_PROJECT_ID=your-project-id \
  -e APIGEE_MCP_APIGEE_ORGANIZATION=your-org-name \
  -e APIGEE_MCP_GOOGLE_CREDENTIALS_PATH=/app/credentials/service-account.json \
  apigee-hybrid-mcp:latest
```

### AWS ECS Deployment

Detailed instructions in [`deployment/ecs/README.md`](deployment/ecs/README.md)

**Quick Start**:

1. Push image to ECR:
   ```bash
   aws ecr get-login-password --region REGION | docker login --username AWS --password-stdin ACCOUNT_ID.dkr.ecr.REGION.amazonaws.com
   docker tag apigee-hybrid-mcp:latest ACCOUNT_ID.dkr.ecr.REGION.amazonaws.com/apigee-hybrid-mcp:latest
   docker push ACCOUNT_ID.dkr.ecr.REGION.amazonaws.com/apigee-hybrid-mcp:latest
   ```

2. Register task definition:
   ```bash
   cd deployment/ecs
   # Update task-definition.json with your values
   aws ecs register-task-definition --cli-input-json file://task-definition.json
   ```

3. Create ECS service:
   ```bash
   aws ecs create-service \
     --cluster your-cluster \
     --service-name apigee-hybrid-mcp \
     --task-definition apigee-hybrid-mcp:1 \
     --desired-count 2 \
     --launch-type FARGATE
   ```

### AWS EKS Deployment with Helm

**Prerequisites**:
- EKS cluster configured
- kubectl configured to access cluster
- Helm 3.x installed

**Deployment Steps**:

1. **Create namespace**:
   ```bash
   kubectl create namespace apigee-mcp
   ```

2. **Create secret with credentials**:
   ```bash
   kubectl create secret generic apigee-mcp-credentials \
     --from-file=service-account.json=credentials/service-account.json \
     -n apigee-mcp
   ```

3. **Update values**:
   ```bash
   cd deployment/kubernetes/helm
   # Edit values.yaml with your configuration
   ```

4. **Install Helm chart**:
   ```bash
   helm install apigee-mcp . \
     --namespace apigee-mcp \
     --set config.googleProjectId=your-project-id \
     --set config.apigeeOrganization=your-org-name
   ```

5. **Verify deployment**:
   ```bash
   kubectl get pods -n apigee-mcp
   kubectl logs -f deployment/apigee-hybrid-mcp -n apigee-mcp
   ```

6. **Upgrade**:
   ```bash
   helm upgrade apigee-mcp . --namespace apigee-mcp
   ```

## 🔌 MCP Integration

### VS Code Integration

1. **Install MCP extension** (if available) or configure manually

2. **Add to VS Code settings** (`.vscode/settings.json`):
   ```json
   {
     "mcp.servers": {
       "apigee": {
         "command": "python",
         "args": ["-m", "apigee_hybrid_mcp.server"],
         "env": {
           "APIGEE_MCP_GOOGLE_PROJECT_ID": "your-project-id",
           "APIGEE_MCP_APIGEE_ORGANIZATION": "your-org-name",
           "APIGEE_MCP_GOOGLE_CREDENTIALS_PATH": "./credentials/service-account.json"
         }
       }
     }
   }
   ```

3. **Use MCP tools** in your code:
   - Type `/mcp` to see available tools
   - Call tools like `list-api-proxies`, `get-developer`, etc.

### Claude Desktop Integration

1. **Edit Claude configuration** (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):
   ```json
   {
     "mcpServers": {
       "apigee": {
         "command": "python",
         "args": ["-m", "apigee_hybrid_mcp.server"],
         "env": {
           "APIGEE_MCP_GOOGLE_PROJECT_ID": "your-project-id",
           "APIGEE_MCP_APIGEE_ORGANIZATION": "your-org-name",
           "APIGEE_MCP_GOOGLE_CREDENTIALS_PATH": "/path/to/service-account.json"
         }
       }
     }
   }
   ```

2. **Restart Claude Desktop**

3. **Use tools** in conversation:
   - "List all API proxies in my organization"
   - "Get details for the weather-api proxy"
   - "Create a new developer with email dev@example.com"

## 📚 API Coverage

Full API documentation is archived in the [`archive/apigee-docs/`](archive/apigee-docs/) directory with timestamps for version tracking.

### Supported Operations

| Resource | Operations | MCP Tools |
|----------|------------|-----------|
| Organizations | List, Get, Update | ✅ `list-organizations`, `get-organization` |
| Environments | List, Get, Create, Update, Delete | ✅ `list-environments`, `get-environment`, `create-environment` |
| API Proxies | List, Get, Deploy, Undeploy | ✅ `list-api-proxies`, `get-api-proxy`, `deploy-api-proxy`, `undeploy-api-proxy` |
| Developers | List, Get, Create, Update, Delete | ✅ `list-developers`, `get-developer`, `create-developer` |
| Developer Apps | List, Get, Create, Update, Delete | ✅ `list-developer-apps`, `get-developer-app`, `create-developer-app` |
| API Products | List, Get, Create, Update, Delete | ✅ `list-api-products`, `get-api-product`, `create-api-product` |
| Shared Flows | List, Get, Deploy, Undeploy | ✅ `list-shared-flows`, `get-shared-flow`, `deploy-shared-flow` |
| Keystores | List, Get, Create, Delete | ✅ `list-keystores`, `get-keystore` |
| Keystore Aliases | List, Get, Create, Update, Delete | ✅ `list-keystore-aliases`, `get-keystore-alias` |
| **Teams** | **List, Get, Create, Update, Delete** | ✅ **`list-teams`, `get-team`, `create-team`, `update-team`, `delete-team`** |
| ~~Companies~~ | ~~List, Get, Create~~ | ⚠️ **DEPRECATED** - Use Teams API instead (Companies are OPDK-only) |
| Debug Sessions | Create, Get Data | ✅ `create-debug-session`, `get-debug-session-data` |

### Teams API

The **Teams API** provides team-based API access management for Apigee Hybrid. This replaces the deprecated Companies API which is only available in Apigee OPDK (On-Premises).

**Key Features:**
- Team creation with unique names and member management
- Built-in validation (team names, email addresses)
- In-memory storage (extensible to datastore)
- Full CRUD operations via MCP tools

**Example Usage:**
```python
# Create a team
create_team(
    name="engineering-team",
    description="Engineering department API access",
    members=["dev1@example.com", "dev2@example.com"]
)

# List all teams
list_teams()

# Update team members
update_team(
    team_id="team-abc123",
    members=["dev1@example.com", "dev2@example.com", "dev3@example.com"]
)

# Delete a team
delete_team(team_id="team-abc123")
```

**Important Notes:**
- ⚠️ The **Companies API** (`list-companies`, `get-company`, `create-company`) is **deprecated** in Apigee Hybrid
- Companies/Organizations in the Apigee sense are only available in Apigee OPDK (on-premises)
- For Apigee Hybrid deployments, use the new **Teams API** for group-based access management


## 🧪 Testing

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/apigee_hybrid_mcp --cov-report=html --cov-report=term

# Run specific test file
pytest tests/unit/test_api_products.py

# Run with verbose output
pytest -v

# Run only unit tests
pytest tests/unit/

# Run only integration tests
pytest tests/integration/
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint code
ruff check src/ tests/

# Type checking
mypy src/
```

### Coverage Report

After running tests with coverage, open `htmlcov/index.html` in your browser to view detailed coverage report.

## 🔒 Security

### Security Features

- ✅ Non-root container user (UID 1000)
- ✅ Read-only root filesystem
- ✅ Dropped all capabilities
- ✅ Secrets via environment variables or mounted volumes
- ✅ TLS/SSL for all API communications
- ✅ Rate limiting to prevent abuse
- ✅ Input validation with Pydantic
- ✅ Structured logging (no sensitive data in logs)

### Best Practices

1. **Credentials**: Never commit credentials to version control
2. **Secrets Management**: Use AWS Secrets Manager or Kubernetes Secrets
3. **IAM**: Follow principle of least privilege for service accounts
4. **Network**: Use private subnets and security groups
5. **Updates**: Regularly update dependencies for security patches

## 📊 Monitoring

### Logging

Structured JSON logging with key fields:
- `timestamp`: ISO 8601 timestamp
- `level`: Log level (DEBUG, INFO, WARNING, ERROR)
- `event`: Event name
- `context`: Additional context (operation, organization, etc.)

Example log entry:
```json
{
  "timestamp": "2024-01-01T00:00:00Z",
  "level": "info",
  "event": "api_request",
  "method": "GET",
  "url": "https://apigee.googleapis.com/v1/organizations/my-org",
  "params": {}
}
```

### Metrics

Key metrics to monitor:
- Request latency
- Error rate
- Circuit breaker state
- Rate limit hits
- API call counts by operation
- Memory and CPU usage

### Health Checks

- **Liveness Probe**: Python interpreter check
- **Readiness Probe**: Python interpreter check
- **Custom Health Endpoint**: (if HTTP mode enabled)

## 🔧 Troubleshooting

### Common Issues

1. **Authentication Errors**:
   - Verify service account has correct permissions
   - Check credentials file path and format
   - Ensure credentials are not expired

2. **Connection Errors**:
   - Verify network connectivity to Apigee APIs
   - Check firewall rules
   - Verify proxy settings (if applicable)

3. **Rate Limiting**:
   - Adjust `RATE_LIMIT_REQUESTS` and `RATE_LIMIT_WINDOW`
   - Implement request batching
   - Use caching where appropriate

4. **Circuit Breaker Open**:
   - Check error logs for underlying issues
   - Verify API endpoints are accessible
   - Wait for circuit breaker timeout

### Debug Mode

Enable debug logging:
```bash
export APIGEE_MCP_LOG_LEVEL=DEBUG
python -m apigee_hybrid_mcp.server
```

### Logs Location

- **Docker**: `docker-compose logs -f`
- **ECS**: CloudWatch Logs `/ecs/apigee-hybrid-mcp`
- **EKS**: `kubectl logs -f deployment/apigee-hybrid-mcp -n apigee-mcp`

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

### Development Setup

1. **Fork and clone the repository**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/apigee-hybrid-mcp.git
   cd apigee-hybrid-mcp
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -e .
   pip install -r requirements-dev.txt
   ```

4. **Install pre-commit hooks** (recommended):
   ```bash
   pip install pre-commit
   pre-commit install
   ```

### Code Quality Standards

This project follows **PEP 8** (Python Enhancement Proposal 8) style guidelines and enforces high code quality standards.

#### Formatting and Linting

- **Black** (code formatter): Automatically formats code to PEP 8 standards
  ```bash
  black src/ tests/ --line-length=100
  ```

- **Ruff** (linter): Fast Python linter replacing flake8, isort, pyupgrade
  ```bash
  ruff check src/ tests/ --fix
  ```

- **MyPy** (type checker): Static type checking
  ```bash
  mypy src/
  ```

#### Documentation Standards

- Follow **PEP 257** for docstrings
- All public modules, classes, and functions must have docstrings
- Use Google-style docstring format with types
- Example:
  ```python
  def create_team(name: str, description: str = "") -> Team:
      """Create a new team.
      
      Args:
          name: Team name (must be unique)
          description: Optional team description
          
      Returns:
          Team: The created team
          
      Raises:
          TeamAlreadyExistsError: If team with name exists
      """
  ```

#### Testing

- Write comprehensive unit tests for all new features
- Aim for >80% code coverage
- Use pytest with async support
- Run tests:
  ```bash
  # Run all tests
  pytest
  
  # Run with coverage
  pytest --cov=src/apigee_hybrid_mcp --cov-report=html --cov-report=term
  
  # Run specific test file
  pytest tests/unit/test_teams.py -v
  ```

#### Pre-commit Hooks

Pre-commit hooks automatically check your code before commits:
- Black formatting
- Ruff linting and import sorting
- MyPy type checking (optional)
- Bandit security checks
- YAML/JSON validation
- Trailing whitespace removal

Run manually:
```bash
pre-commit run --all-files
```

### Contribution Workflow

1. Create a feature branch (`git checkout -b feature/amazing-feature`)
2. Write tests for your changes
3. Implement your feature
4. Run code quality checks:
   ```bash
   black src/ tests/
   ruff check src/ tests/ --fix
   mypy src/
   pytest
   ```
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request with a clear description

### Code Review

All submissions require review. We use GitHub pull requests for this purpose. Consult
[GitHub Help](https://help.github.com/articles/about-pull-requests/) for more information on using pull requests.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
- [Google Cloud Apigee](https://cloud.google.com/apigee)
- [Anthropic](https://www.anthropic.com/)
- Society for Conservation GIS Wales

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/SCGIS-Wales/apigee-hybrid-mcp/issues)
- **Documentation**: [API Documentation Archive](archive/apigee-docs/)
- **Email**: info@scgis.wales

---

**Built with ❤️ by Society for Conservation GIS Wales**
