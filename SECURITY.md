# Security Policy

## Supported Versions

We release patches for security vulnerabilities. Currently supported versions:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take the security of Apigee Hybrid MCP Server seriously. If you believe you have found a security vulnerability, please report it to us as described below.

### Reporting Process

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report them via email to: **security@scgis.wales**

You should receive a response within 48 hours. If for some reason you do not, please follow up via email to ensure we received your original message.

Please include the following information in your report:

- Type of issue (e.g., buffer overflow, SQL injection, cross-site scripting, etc.)
- Full paths of source file(s) related to the manifestation of the issue
- The location of the affected source code (tag/branch/commit or direct URL)
- Any special configuration required to reproduce the issue
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue, including how an attacker might exploit it

This information will help us triage your report more quickly.

### What to Expect

- **Initial Response**: Within 48 hours
- **Status Updates**: We'll keep you informed about the progress
- **Fix Timeline**: We aim to release security patches within 7 days for critical issues
- **Credit**: We'll acknowledge your contribution in the security advisory (unless you prefer to remain anonymous)

## Security Update Process

1. Security vulnerability is reported and confirmed
2. Fix is developed and tested
3. Security advisory is prepared
4. New version is released with security patch
5. Security advisory is published
6. Users are notified through GitHub releases and security advisories

## Security Best Practices for Users

### Container Security

1. **Always use specific version tags**, never use `latest` in production
2. **Scan images regularly** for vulnerabilities:
   ```bash
   trivy image ghcr.io/scgis-wales/apigee-hybrid-mcp:1.0.0
   ```
3. **Verify image signatures**:
   ```bash
   cosign verify ghcr.io/scgis-wales/apigee-hybrid-mcp:1.0.0
   ```

### Kubernetes Security

1. **Use Network Policies** to restrict pod communication
2. **Enable Pod Security Standards**:
   ```yaml
   apiVersion: v1
   kind: Namespace
   metadata:
     name: apigee-mcp
     labels:
       pod-security.kubernetes.io/enforce: restricted
   ```
3. **Use Secrets for sensitive data**:
   ```bash
   kubectl create secret generic apigee-mcp-credentials \
     --from-file=service-account.json
   ```
4. **Limit resource consumption**:
   ```yaml
   resources:
     limits:
       cpu: 1000m
       memory: 1024Mi
     requests:
       cpu: 500m
       memory: 512Mi
   ```

### Application Security

1. **Rotate credentials regularly** (at least every 90 days)
2. **Use least privilege IAM roles**
3. **Enable audit logging**:
   ```yaml
   env:
   - name: APIGEE_MCP_LOG_LEVEL
     value: "INFO"
   ```
4. **Monitor for suspicious activity**
5. **Keep dependencies updated**:
   ```bash
   pip list --outdated
   pip-audit
   ```

### Network Security

1. **Use TLS for all communications**
2. **Implement network segmentation**
3. **Use private subnets** for container deployment
4. **Configure security groups/firewall rules** to allow only necessary traffic

## Security Features

### Built-in Security

- ✅ Non-root container user (UID 1000)
- ✅ Read-only root filesystem
- ✅ Dropped all Linux capabilities
- ✅ Security contexts enforced
- ✅ No shell in container (`/sbin/nologin`)
- ✅ Minimal base image (Python 3.14-slim)
- ✅ Automated vulnerability scanning
- ✅ Signed container images
- ✅ Secrets management support
- ✅ Network policies
- ✅ Pod disruption budgets
- ✅ Resource limits
- ✅ Structured logging (no sensitive data)

### Compliance

This project follows:
- OWASP Top 10 security guidelines
- CIS Docker Benchmark
- Kubernetes Pod Security Standards (Restricted)
- NIST Cybersecurity Framework

## Known Security Considerations

1. **Google Cloud Credentials**: Service account keys should be protected as secrets
2. **Rate Limiting**: Default rate limits are configured but should be adjusted based on usage
3. **Network Exposure**: MCP server uses stdio by default (no network exposure)
4. **Logging**: Ensure logs don't contain sensitive data (structured logging helps)

## Security Scanning

### Automated Scans

Every release is automatically scanned for:
- Container vulnerabilities (Trivy)
- Dependency vulnerabilities (Safety, pip-audit)
- Code security issues (Bandit)
- Static analysis (ruff, mypy)

### Manual Security Testing

Before major releases, we conduct:
- Penetration testing
- Security code review
- Dependency audit
- Configuration review

## Third-Party Security Tools

We recommend using these tools:

- **Container Scanning**: Trivy, Grype, Clair
- **Dependency Scanning**: Safety, pip-audit, Snyk
- **Code Analysis**: Bandit, Semgrep, SonarQube
- **Runtime Security**: Falco, Sysdig, Aqua Security
- **Secrets Detection**: TruffleHog, GitLeaks

## Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CIS Docker Benchmark](https://www.cisecurity.org/benchmark/docker)
- [Kubernetes Security Best Practices](https://kubernetes.io/docs/concepts/security/)
- [Google Cloud Security Best Practices](https://cloud.google.com/security/best-practices)

## Contact

For security-related questions or concerns:
- Email: security@scgis.wales
- GPG Key: [Available on request]

---

**Remember**: Security is a shared responsibility. While we strive to make this software secure, proper deployment and operational security are equally important.
