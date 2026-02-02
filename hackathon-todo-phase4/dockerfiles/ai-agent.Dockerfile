# Dockerfile for ai-agent (with MCP server support)

# Use multi-stage build for optimized production image
# Stage 1: Build/Dependency installation
FROM python:3.13-slim as builder

# Install system dependencies needed for AI/ML packages
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    gfortran \
    build-essential \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml poetry.lock* ./

# Install poetry and create virtual environment
RUN pip install poetry
ENV POETRY_VENV_IN_PROJECT=true
ENV POETRY_NO_INTERACTION=1
ENV POETRY_CACHE_DIR=/tmp/poetry_cache

# Install dependencies
RUN poetry install --only=main --no-root

# Stage 2: Production image
FROM python:3.13-slim

# Install minimal system dependencies
RUN apt-get update && apt-get install -y \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set working directory
WORKDIR /app

# Copy Python environment from builder stage
COPY --from=builder --chown=appuser:appuser /app/.venv /app/.venv

# Copy application code
COPY --chown=appuser:appuser . .

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app:$PYTHONPATH"

# Switch to non-root user
USER appuser

# Expose port for MCP server
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

# Command to run the AI agent with MCP support
CMD ["python", "src/ai_agent.py"]