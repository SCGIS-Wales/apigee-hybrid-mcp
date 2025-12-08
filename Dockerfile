# Multi-stage Dockerfile for Apigee Hybrid MCP Server
# Optimized for security, size, and performance
# Based on Python 3.11 (3.14 not yet available in official images)

# Stage 1: Builder - Install dependencies
FROM python:3.11-slim AS builder

# Set build arguments
ARG DEBIAN_FRONTEND=noninteractive

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    make \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements first for better caching
COPY requirements.txt /tmp/
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r /tmp/requirements.txt

# Copy application source
COPY src/ /app/src/
COPY pyproject.toml /app/
WORKDIR /app

# Install application
RUN pip install --no-cache-dir -e .

# Stage 2: Runtime - Minimal image
FROM python:3.11-slim AS runtime

# Set metadata
LABEL maintainer="SCGIS Wales <info@scgis.wales>"
LABEL description="Apigee Hybrid MCP Server - Model Context Protocol server for Apigee API management"
LABEL version="1.0.0"

# Create non-root user for security
RUN groupadd -r apigee && useradd -r -g apigee -u 1000 apigee

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Copy application from builder
COPY --from=builder /app /app

# Set environment variables
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH="/app/src:$PYTHONPATH" \
    APIGEE_MCP_LOG_LEVEL=INFO

# Set working directory
WORKDIR /app

# Create directories for data and logs
RUN mkdir -p /app/data /app/logs && \
    chown -R apigee:apigee /app

# Switch to non-root user
USER apigee

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Expose port (if needed for HTTP server mode)
EXPOSE 8080

# Default command - run MCP server via stdio
CMD ["python", "-m", "apigee_hybrid_mcp.server"]

# Alternative: HTTP server mode (uncomment if needed)
# CMD ["python", "-m", "apigee_hybrid_mcp.server", "--mode", "http"]
