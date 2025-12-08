# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Additional unit tests for remaining modules

### Changed
- Performance optimizations

## [1.0.0] - 2025-12-08

### Added
- Initial release of Apigee Hybrid MCP Server
- Comprehensive MCP server with 30+ tools for Apigee Hybrid APIs
- Functional Python programming implementation
- Organizations API support
- Environments API support
- API Proxies lifecycle management (deploy, undeploy, revisions)
- Developers API support
- Developer Apps and Company Apps management
- API Products with quotas and rate limits
- Shared Flows support
- Keystores and Truststores management with aliases
- Companies (Teams) API support
- Debug Sessions (Trace) API support
- Production-grade resilience patterns:
  - Circuit breakers
  - Exponential backoff retry logic
  - Rate limiting
  - Structured logging (JSON)
- Security-hardened Docker container:
  - Multi-stage build
  - Non-root user (UID 1000)
  - Read-only root filesystem
  - Dropped all capabilities
  - Minimal base image (Python 3.14-slim)
- AWS deployment configurations:
  - ECS task definition
  - EKS Helm chart
- Kubernetes features:
  - Horizontal Pod Autoscaler (75% CPU threshold)
  - Pod Disruption Budget
  - Network Policies
  - Security contexts
  - Service Account with automount disabled
- Comprehensive testing infrastructure:
  - pytest configuration
  - Unit tests with fixtures
  - Test coverage reporting
  - Static code analysis (ruff, mypy, black)
- GitHub Actions CI/CD:
  - Automated testing
  - Security scanning (Trivy, Bandit, Safety)
  - Multi-architecture builds (amd64, arm64)
  - GitHub Container Registry publishing
  - Cosign image signing
  - Automated releases with semantic versioning
  - Helm chart publishing to OCI registry
- Documentation:
  - Comprehensive README (400+ lines)
  - API documentation archive with timestamps
  - Deployment guides (Docker, ECS, EKS)
  - MCP integration guides (VS Code, Claude Desktop)
  - Security best practices
  - Monitoring and troubleshooting guides
- Example configurations:
  - `.env.example` for local development
  - Docker Compose for local testing
  - Helm values for Kubernetes deployment

### Security
- Container image scanned with Trivy
- Dependencies scanned with Safety
- Code scanned with Bandit
- Images signed with Cosign
- Security contexts enforced in Kubernetes
- Non-root container user
- Read-only root filesystem
- Network policies for pod isolation

[Unreleased]: https://github.com/SCGIS-Wales/apigee-hybrid-mcp/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/SCGIS-Wales/apigee-hybrid-mcp/releases/tag/v1.0.0
