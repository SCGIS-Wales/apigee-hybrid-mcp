# Multi-stage Dockerfile for Apigee Hybrid MCP Server
# Security-hardened for production use
# Based on Python 3.14

# Stage 1: Builder - Install dependencies
FROM python:3.14-slim AS builder

# Set build arguments for metadata
ARG BUILD_DATE
ARG VCS_REF
ARG VERSION=1.0.0

# Set labels for OCI image spec
LABEL org.opencontainers.image.created="${BUILD_DATE}" \
      org.opencontainers.image.authors="SCGIS Wales <info@scgis.wales>" \
      org.opencontainers.image.url="https://github.com/SCGIS-Wales/apigee-hybrid-mcp" \
      org.opencontainers.image.source="https://github.com/SCGIS-Wales/apigee-hybrid-mcp" \
      org.opencontainers.image.version="${VERSION}" \
      org.opencontainers.image.revision="${VCS_REF}" \
      org.opencontainers.image.vendor="SCGIS Wales" \
      org.opencontainers.image.title="Apigee Hybrid MCP Server" \
      org.opencontainers.image.description="MCP server for Google Apigee Hybrid API management" \
      org.opencontainers.image.licenses="MIT"

# Set build environment
ARG DEBIAN_FRONTEND=noninteractive

# Install build dependencies with specific versions for security
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc=4:12.2.0-3 \
    g++=4:12.2.0-3 \
    make=4.3-4.1 \
    libffi-dev=3.4.4-1 \
    libssl-dev=3.0.11-1~deb12u2 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create virtual environment with specific Python version
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Upgrade pip, setuptools, and wheel to latest secure versions
RUN pip install --no-cache-dir --upgrade \
    pip==24.0 \
    setuptools==69.5.1 \
    wheel==0.43.0

# Copy requirements first for better layer caching
COPY requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Copy application source
COPY src/ /app/src/
COPY pyproject.toml README.md LICENSE /app/
WORKDIR /app

# Install application
RUN pip install --no-cache-dir -e .

# Remove build artifacts and temporary files
RUN find /opt/venv -type d -name '__pycache__' -exec rm -rf {} + && \
    find /opt/venv -type f -name '*.pyc' -delete && \
    find /opt/venv -type f -name '*.pyo' -delete

# Stage 2: Runtime - Security-hardened minimal image
FROM python:3.14-slim AS runtime

# Set metadata
LABEL maintainer="SCGIS Wales <info@scgis.wales>" \
      description="Apigee Hybrid MCP Server - Model Context Protocol server for Apigee API management" \
      version="1.0.0"

# Install runtime dependencies only (no build tools)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates=20230311 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user and group with specific UID/GID for security
RUN groupadd -r -g 1000 apigee && \
    useradd -r -u 1000 -g apigee -s /sbin/nologin -c "Apigee MCP User" apigee

# Copy virtual environment from builder
COPY --from=builder --chown=apigee:apigee /opt/venv /opt/venv

# Copy application from builder
COPY --from=builder --chown=apigee:apigee /app /app

# Set environment variables for security and performance
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH="/app/src:$PYTHONPATH" \
    APIGEE_MCP_LOG_LEVEL=INFO \
    PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set working directory
WORKDIR /app

# Create directories for data and logs with correct permissions
RUN mkdir -p /app/data /app/logs /tmp && \
    chown -R apigee:apigee /app /tmp && \
    chmod 755 /app && \
    chmod 1777 /tmp

# Switch to non-root user
USER apigee

# Health check with timeout
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import sys; from apigee_hybrid_mcp import __version__; sys.exit(0)" || exit 1

# Expose port (if needed for HTTP server mode)
EXPOSE 8080

# Set stop signal
STOPSIGNAL SIGTERM

# Default command - run MCP server via stdio
CMD ["python", "-m", "apigee_hybrid_mcp.server"]
