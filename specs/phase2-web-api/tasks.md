# Phase 2 Web API Tasks

## Task 1: Install Dependencies [x]
- **Description**: Install FastAPI and Uvicorn using uv
- **Command**: `uv add fastapi uvicorn`
- **Steps**:
  - Run the uv add command to install FastAPI and Uvicorn
  - Verify the dependencies are added to pyproject.toml
  - Confirm that the virtual environment is updated
- **Definition of Done**:
  - FastAPI and Uvicorn are installed in the project
  - Dependencies are listed in pyproject.toml
  - Virtual environment is properly configured with new packages

## Task 2: Create API Models [x]
- **Description**: Define Pydantic models for API requests and responses
- **Steps**:
  - Create src/api_models.py
  - Define TaskRequest model for creation/updating tasks
  - Define TaskResponse model for returning tasks
  - Define ErrorResponse model for error responses
- **Definition of Done**:
  - All required Pydantic models are defined
  - Models include proper validation rules
  - Models follow the API specification

## Task 3: Create FastAPI Application [x]
- **Description**: Set up the FastAPI application with all required endpoints
- **Steps**:
  - Create src/api.py
  - Initialize FastAPI app instance
  - Implement POST /tasks endpoint
  - Implement GET /tasks endpoint
  - Implement PUT /tasks/{id} endpoint
  - Implement DELETE /tasks/{id} endpoint
  - Implement PATCH /tasks/{id}/toggle endpoint
- **Definition of Done**:
  - All 5 required endpoints are implemented
  - Each endpoint connects to the appropriate service function
  - Proper HTTP status codes are returned
  - Error handling is implemented

## Task 4: Test API Endpoints [x]
- **Description**: Create tests for all API endpoints
- **Steps**:
  - Create tests/test_api.py
  - Use FastAPI's TestClient for testing
  - Test successful requests for each endpoint
  - Test error conditions and validation
  - Verify integration with service layer
- **Definition of Done**:
  - All API endpoints have comprehensive tests
  - Tests cover success and error scenarios
  - All tests pass successfully

## Task 5: Run and Verify API [x]
- **Description**: Start the API server and verify functionality
- **Steps**:
  - Run the API using uvicorn
  - Test endpoints using the built-in Swagger UI
  - Verify all functionality works as expected
- **Definition of Done**:
  - API server starts successfully
  - All endpoints function correctly
  - Interactive documentation is available