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
- **Comprehensive API Coverage**: All major Apigee Hybrid APIs (Organizations, Environments, API Proxies, Developers, Apps, API Products, Shared Flows, Keystores, Debug Sessions)
- **Custom Teams API**: Team-based organizational management (custom implementation for Hybrid)
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
- ✅ **Teams**: Custom team-based organizational management (Hybrid-specific)
- ✅ **Debug Sessions (Trace)**: Request tracing and troubleshooting

**Note**: Teams API is a custom implementation for Apigee Hybrid. Unlike Apigee OPDK (which has "companies"), Apigee Hybrid does not provide a native companies/teams API. This implementation provides in-memory team management suitable for organizational needs.

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
| Teams | List, Get, Create, Update, Delete | ✅ `list-teams`, `get-team`, `create-team`, `update-team`, `delete-team` |
| Debug Sessions | Create, Get Data | ✅ `create-debug-session`, `get-debug-session-data` |

**Note**: The Teams API is a custom implementation for organizational management in Apigee Hybrid. It provides in-memory storage and is not part of the native Apigee API.

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

## 🚨 Error Handling

The MCP server provides comprehensive error handling with structured error responses, correlation IDs for tracking, and automatic sensitive data redaction.

### Error Response Format

All errors follow a consistent JSON structure:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "status": 400,
    "details": {
      "parameter": "param_name",
      "additional": "context"
    },
    "correlation_id": "uuid-for-tracking"
  }
}
```

### Error Categories

| Status Code | Error Type | Description |
|-------------|------------|-------------|
| 401 | Authentication | Invalid or missing credentials |
| 403 | Authorization | Insufficient permissions |
| 404 | Not Found | Resource doesn't exist |
| 408 | Timeout | Operation exceeded timeout |
| 409 | Conflict | Resource already exists |
| 422 | Validation | Parameter validation failed |
| 429 | Rate Limit | Too many requests |
| 500 | Server Error | Internal server error |
| 502 | Bad Gateway | External service error |
| 503 | Service Unavailable | Service temporarily down |

### Common Error Codes

- `INVALID_PARAMETER`: Parameter value is invalid
- `MISSING_PARAMETER`: Required parameter not provided
- `EXPIRED_PARAMETER`: Time-bound parameter has expired
- `AUTHENTICATION_ERROR`: Authentication failed
- `AUTHORIZATION_ERROR`: Access denied
- `RESOURCE_NOT_FOUND`: Resource doesn't exist
- `RESOURCE_ALREADY_EXISTS`: Resource already exists
- `TIMEOUT_ERROR`: Operation timed out
- `EXTERNAL_SERVICE_ERROR`: External service failure

### Example Error Responses

**Missing Parameter (422):**
```json
{
  "error": {
    "code": "MISSING_PARAMETER",
    "message": "Missing required parameter: 'organization'",
    "status": 422,
    "details": {
      "parameter": "organization"
    },
    "correlation_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
  }
}
```

**Resource Not Found (404):**
```json
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "Team not found: team-123",
    "status": 404,
    "details": {
      "resource_type": "team",
      "resource_id": "team-123"
    },
    "correlation_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
  }
}
```

**Authentication Error (401):**
```json
{
  "error": {
    "code": "AUTHENTICATION_ERROR",
    "message": "Authentication failed",
    "status": 401,
    "details": {
      "reason": "token_expired"
    },
    "correlation_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
  }
}
```

### Correlation IDs

Every error includes a unique `correlation_id` (UUID) for tracking. When reporting issues:

1. Include the full correlation ID
2. Provide the timestamp
3. Describe the operation that failed

### Sensitive Data Redaction

Sensitive fields (tokens, passwords, keys, credentials) are automatically redacted in:
- Error details
- Log messages
- Debug output

For complete error code reference, see [ERROR_CODES.md](docs/ERROR_CODES.md).

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

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Write tests for your changes
4. Ensure all tests pass (`pytest`)
5. Run code quality checks (`black`, `ruff`, `mypy`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

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
