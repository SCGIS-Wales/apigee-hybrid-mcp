# Apigee Hybrid MCP Server - Project Summary

## 🎯 Project Overview

A production-ready, security-hardened Model Context Protocol (MCP) server for Google Apigee Hybrid API management, built with functional Python 3.14 programming principles.

**Repository**: https://github.com/SCGIS-Wales/apigee-hybrid-mcp
**Container Registry**: ghcr.io/scgis-wales/apigee-hybrid-mcp
**Version**: 1.0.0 (Semantic Versioning)

## ✨ Key Features Implemented

### 1. Comprehensive API Coverage
- ✅ 30+ MCP tools covering all major Apigee Hybrid APIs
- ✅ Organizations, Environments, API Proxies, Developers, Apps
- ✅ API Products, Shared Flows, Keystores, Companies, Debug Sessions
- ✅ Full lifecycle management (create, read, update, delete, deploy)

### 2. Functional Programming Design
- ✅ Pure functions with no side effects
- ✅ Immutable data structures
- ✅ Explicit error handling
- ✅ Type hints throughout
- ✅ Comprehensive inline documentation

### 3. Production-Grade Resilience
- ✅ Circuit breakers (5 failures threshold, 60s timeout)
- ✅ Exponential backoff retry logic (3 attempts, 2x multiplier)
- ✅ Rate limiting (100 requests per 60s window)
- ✅ Connection pooling and timeouts (30s)
- ✅ Structured JSON logging

### 4. Security Hardening
- ✅ Non-root container user (UID 1000)
- ✅ Read-only root filesystem
- ✅ Dropped all Linux capabilities
- ✅ Security contexts enforced in Kubernetes
- ✅ Network policies for pod isolation
- ✅ Secrets management via Kubernetes secrets
- ✅ Container image scanning (Trivy)
- ✅ Dependency scanning (Safety, pip-audit)
- ✅ Code security scanning (Bandit)
- ✅ Image signing with Cosign

### 5. Containerization
- ✅ Multi-stage Dockerfile (Python 3.14-slim)
- ✅ Multi-architecture builds (amd64, arm64)
- ✅ Optimized layer caching
- ✅ Minimal image size
- ✅ OCI image labels and metadata
- ✅ Health checks implemented
- ✅ Docker Compose for local development

### 6. Kubernetes Deployment
- ✅ Complete Helm chart with best practices
- ✅ Horizontal Pod Autoscaler (75% CPU, 80% memory)
- ✅ Pod Disruption Budget (min 1 available)
- ✅ Network Policies for isolation
- ✅ Resource limits and requests
- ✅ Service account with automount disabled
- ✅ Security contexts (runAsNonRoot, readOnlyRootFilesystem)
- ✅ Configurable via Helm values

### 7. AWS Deployment
- ✅ ECS task definition (Fargate)
- ✅ EKS-ready with Helm
- ✅ Secrets Manager integration
- ✅ CloudWatch logging
- ✅ Auto-scaling configuration
- ✅ Deployment documentation

### 8. CI/CD Automation
- ✅ GitHub Actions workflow
- ✅ Automated testing (pytest with coverage)
- ✅ Code quality checks (black, ruff, mypy)
- ✅ Security scanning (Trivy, Bandit, Safety)
- ✅ Multi-architecture container builds
- ✅ GitHub Container Registry publishing
- ✅ Image signing with Cosign
- ✅ Automated releases with semantic versioning
- ✅ Helm chart publishing to OCI registry
- ✅ Automated version bumping

### 9. Testing Infrastructure
- ✅ pytest configuration
- ✅ Comprehensive fixtures for all resources
- ✅ Unit tests for:
  - API Products (10+ test cases)
  - Developers
  - Proxy lifecycle
  - Keystores and aliases
  - Debug sessions (Trace)
- ✅ Test coverage reporting
- ✅ Mocking for external dependencies

### 10. Documentation
- ✅ Comprehensive README.md (500+ lines)
  - Installation guides
  - Configuration examples
  - Usage instructions
  - Deployment guides (Docker, ECS, EKS)
  - MCP integration (VS Code, Claude Desktop)
  - API coverage table
  - Testing instructions
  - Security best practices
  - Monitoring and troubleshooting
- ✅ API Documentation Archive (timestamped: 2025-12-08_21-42-21_UTC)
  - 10 comprehensive API reference documents
  - Examples for all operations
  - Error codes and best practices
  - Schema definitions
- ✅ CHANGELOG.md (semantic versioning)
- ✅ SECURITY.md (vulnerability reporting process)
- ✅ CONTRIBUTING.md (development guidelines)
- ✅ Inline code documentation (docstrings everywhere)

## 📊 Project Statistics

### Code Metrics
- **Total Files**: 60+
- **Python Modules**: 15+
- **MCP Tools**: 30+
- **Unit Tests**: 20+
- **Documentation Files**: 15+
- **Lines of Documentation**: 2000+

### API Coverage
| Category | APIs Covered | Tools |
|----------|--------------|-------|
| Management | Organizations, Environments | 5 |
| Proxies | API Proxies, Shared Flows | 8 |
| Developers | Developers, Apps (dev & company) | 8 |
| Products | API Products | 3 |
| Security | Keystores, Truststores, Aliases | 4 |
| Teams | Companies | 3 |
| Debug | Debug Sessions, Trace | 2 |
| **Total** | **10 API Categories** | **30+ Tools** |

### Security Measures
- 🔒 Container Security: 8 hardening measures
- 🔒 Kubernetes Security: 6 security policies
- 🔒 CI/CD Security: 4 scanning tools
- 🔒 Code Security: Static analysis enabled
- 🔒 Secrets: Kubernetes secrets integration
- 🔒 Network: Network policies configured
- 🔒 Image: Signed with Cosign

### Scalability Features
- ⚡ Horizontal Pod Autoscaler (2-10 replicas)
- ⚡ CPU-based scaling (75% threshold)
- ⚡ Memory-based scaling (80% threshold)
- ⚡ Fast scale-up (100% in 30s)
- ⚡ Conservative scale-down (50% in 60s)
- ⚡ Pod Disruption Budget (HA)

## 🚀 Quick Start

### Pull Image
```bash
docker pull ghcr.io/scgis-wales/apigee-hybrid-mcp:1.0.0
```

### Install with Helm
```bash
helm install apigee-mcp oci://ghcr.io/scgis-wales/apigee-hybrid-mcp/charts/apigee-hybrid-mcp \
  --version 1.0.0 \
  --namespace apigee-mcp \
  --create-namespace \
  --set config.googleProjectId=your-project-id \
  --set config.apigeeOrganization=your-org-name
```

### Local Development
```bash
git clone https://github.com/SCGIS-Wales/apigee-hybrid-mcp.git
cd apigee-hybrid-mcp
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m apigee_hybrid_mcp.server
```

## 📋 Release Process

### Manual Release
```bash
# 1. Update VERSION file
echo "1.1.0" > VERSION

# 2. Update CHANGELOG.md
# Add changes under [Unreleased]

# 3. Create and push tag
git tag -a v1.1.0 -m "Release version 1.1.0"
git push origin v1.1.0
```

### Automated by GitHub Actions
- ✅ Tests run automatically
- ✅ Security scans complete
- ✅ Multi-arch images built
- ✅ Images pushed to ghcr.io
- ✅ Images signed with Cosign
- ✅ GitHub release created
- ✅ Helm chart published
- ✅ Version updated in charts

## 🔐 Security

### Vulnerability Reporting
Report security issues to: security@scgis.wales

### Security Scanning
All releases are scanned for:
- Container vulnerabilities (Trivy)
- Dependency vulnerabilities (Safety)
- Code security issues (Bandit)
- Static analysis (ruff, mypy)

### Image Verification
```bash
# Verify image signature
cosign verify ghcr.io/scgis-wales/apigee-hybrid-mcp:1.0.0

# Scan for vulnerabilities
trivy image ghcr.io/scgis-wales/apigee-hybrid-mcp:1.0.0
```

## 📈 Monitoring

### Key Metrics
- Request latency
- Error rate
- Circuit breaker state
- Rate limit hits
- CPU/Memory utilization
- Pod count (autoscaling)

### Logs
- Format: Structured JSON
- Level: Configurable (DEBUG, INFO, WARNING, ERROR)
- Destination: stdout (CloudWatch, EKS logs)

### Health Checks
- Liveness: Python interpreter check
- Readiness: Python interpreter check
- Interval: 30s
- Timeout: 10s

## 🎓 MCP Integration

### VS Code
Add to `.vscode/settings.json`:
```json
{
  "mcp.servers": {
    "apigee": {
      "command": "docker",
      "args": ["run", "-i", "--rm", 
               "-e", "APIGEE_MCP_GOOGLE_PROJECT_ID=...",
               "-v", "./credentials:/app/credentials:ro",
               "ghcr.io/scgis-wales/apigee-hybrid-mcp:1.0.0"]
    }
  }
}
```

### Claude Desktop
Edit `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "apigee": {
      "command": "docker",
      "args": ["run", "-i", "--rm",
               "-e", "APIGEE_MCP_GOOGLE_PROJECT_ID=...",
               "ghcr.io/scgis-wales/apigee-hybrid-mcp:1.0.0"]
    }
  }
}
```

## 🛠️ Technology Stack

- **Language**: Python 3.14
- **Framework**: MCP SDK 1.0.0+
- **HTTP Client**: aiohttp 3.10.0+
- **Validation**: Pydantic 2.9.0+
- **Testing**: pytest 8.3.0+
- **Code Quality**: black, ruff, mypy
- **Container**: Docker with multi-stage builds
- **Orchestration**: Kubernetes with Helm
- **CI/CD**: GitHub Actions
- **Registry**: GitHub Container Registry (ghcr.io)
- **Security**: Trivy, Bandit, Safety, Cosign

## 📝 License

MIT License - See LICENSE file for details

## 🙏 Credits

- **Maintainer**: Society for Conservation GIS Wales
- **MCP Protocol**: Anthropic
- **Apigee API**: Google Cloud
- **Contributors**: See CONTRIBUTING.md

## 📞 Support

- **Issues**: https://github.com/SCGIS-Wales/apigee-hybrid-mcp/issues
- **Discussions**: https://github.com/SCGIS-Wales/apigee-hybrid-mcp/discussions
- **Email**: info@scgis.wales
- **Security**: security@scgis.wales

---

**Status**: ✅ Production Ready
**Version**: 1.0.0
**Last Updated**: 2025-12-08
**Build**: Automated with GitHub Actions
**Container**: ghcr.io/scgis-wales/apigee-hybrid-mcp:1.0.0
