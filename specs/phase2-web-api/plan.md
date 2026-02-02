# Phase 2 Web API Implementation Plan

## Overview
This plan outlines how we will evolve our existing CLI application into a web API using FastAPI. We will maintain the in-memory storage approach and reuse our existing service layer logic.

## Architecture Approach
- **FastAPI Framework**: Use FastAPI to create REST API endpoints
- **Service Layer Reuse**: Leverage existing functions from `src/services.py`
- **In-Memory Storage**: Continue using the same in-memory storage from Phase 1
- **Pydantic Models**: Define request/response models for data validation

## Implementation Steps

### 1. Dependencies Setup
- Install FastAPI and Uvicorn using `uv add fastapi uvicorn`
- Update pyproject.toml with new dependencies

### 2. Pydantic Models
- Create `src/api_models.py` with Pydantic models for:
  - TaskRequest: For task creation/update requests
  - TaskResponse: For task response objects
  - ErrorResponse: For error responses

### 3. API Endpoints Implementation
- Create `src/api.py` with FastAPI app instance
- Implement the 5 required endpoints:
  - POST /tasks
  - GET /tasks
  - PUT /tasks/{id}
  - DELETE /tasks/{id}
  - PATCH /tasks/{id}/toggle
- Connect each endpoint to the corresponding service function

### 4. Error Handling
- Implement proper HTTP status codes
- Handle validation errors
- Implement custom exception handlers

### 5. Documentation
- FastAPI will automatically generate interactive API documentation (Swagger UI and ReDoc)
- Ensure all endpoints are properly documented with descriptions

## Technical Details

### API Structure
```
src/
├── models.py          # (from Phase 1, unchanged)
├── services.py        # (from Phase 1, unchanged)
├── api_models.py      # (new) Pydantic models for API
├── api.py            # (new) FastAPI application
└── cli.py            # (from Phase 1, unchanged)
```

### Data Flow
1. API endpoint receives request
2. Request validated against Pydantic model
3. Call corresponding function in services.py
4. Return response formatted as Pydantic model

### FastAPI Features to Utilize
- Dependency injection for service functions
- Automatic request/response validation
- Automatic API documentation generation
- Type hints and Pydantic models for data validation

## Testing Strategy
- Use FastAPI's TestClient for API testing
- Create tests for all endpoints
- Verify integration with existing service functions
- Test error conditions and edge cases

## Constitution Compliance
- Python 3.13: Continue using Python 3.13
- PEP 8: Follow Python style guidelines
- In-Memory Storage: Maintain in-memory approach (no database)