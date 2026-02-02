# Containerization Plan for Todo Evolution - Phase 4

## Overview
This document outlines the containerization strategy for the Todo Evolution application components:
1. todo-backend (FastAPI)
2. todo-frontend (Next.js)
3. ai-agent (with MCP server support)

## Component 1: todo-backend (FastAPI)

### Dockerfile Strategy
- Base image: python:3.13-slim for optimized size
- Multi-stage build to minimize attack surface
- Copy requirements first for better layer caching
- Install only production dependencies
- Use non-root user for security
- Expose port 8000 (default FastAPI port)

### Environment Variables Needed
- DATABASE_URL: Connection string for Neon/PostgreSQL
- ENVIRONMENT: Development/Production flag
- LOG_LEVEL: Logging level configuration

### Build Process
1. Create requirements.txt from pyproject.toml
2. Copy requirements and install dependencies
3. Copy application code
4. Set up non-root user
5. Configure entrypoint and health check

## Component 2: todo-frontend (Next.js)

### Dockerfile Strategy
- Multi-stage build: build stage and production stage
- Build stage: node:18-alpine with dependencies and build
- Production stage: node:18-alpine-slim with only production files
- Use nginx for static file serving in production
- Optimize for size and security

### Environment Variables Needed
- NEXT_PUBLIC_API_URL: URL of the backend API
- NEXT_PUBLIC_APP_NAME: Application name
- Other Next.js public environment variables

### Build Process
1. Install dependencies in build stage
2. Build the Next.js application
3. Copy build artifacts to production stage
4. Configure nginx to serve static files
5. Set up health checks

## Component 3: ai-agent (with MCP server support)

### Dockerfile Strategy
- Base image: python:3.13-slim
- Install AI/ML dependencies (transformers, torch, etc.)
- Include MCP server components
- Multi-stage build if possible
- Use non-root user for security
- Expose MCP server port

### Environment Variables Needed
- MCP_SERVER_URL: URL for MCP server
- AI_MODEL_PATH: Path to AI models
- API_KEYS: Various API keys for AI services
- MCP_CONFIG_PATH: Path to MCP configuration

### Build Process
1. Install base Python dependencies
2. Install AI/ML specific dependencies
3. Copy AI models (if needed) or download during build
4. Configure MCP server
5. Set up entrypoint and health check

## Common Containerization Practices

### Security
- Use non-root users in all containers
- Scan images for vulnerabilities
- Use minimal base images
- Implement .dockerignore files to exclude sensitive files

### Optimization
- Multi-stage builds to reduce image size
- Layer caching through proper Dockerfile structure
- Use .dockerignore to exclude unnecessary files
- Regular base image updates

### Health Checks
- Implement liveness and readiness probes
- Create dedicated health check endpoints where possible
- Configure appropriate timeouts and intervals

### Resource Management
- Define resource limits and requests
- Configure appropriate CPU and memory allocation
- Set up resource quotas at the namespace level

## Testing Strategy
- Test each container individually
- Test container communication
- Verify environment variable handling
- Validate security configurations
- Performance testing of containerized services