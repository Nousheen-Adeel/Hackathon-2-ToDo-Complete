# Phase 3 Database Integration Tasks

## Task T-001: Install Dependencies [x]
- **Description**: Install SQLAlchemy and psycopg2-binary using uv
- **Command**: `uv add sqlalchemy psycopg2-binary`
- **Steps**:
  - Run the uv add command to install SQLAlchemy and psycopg2-binary
  - Verify the dependencies are added to pyproject.toml
  - Confirm that the virtual environment is updated
- **Definition of Done**:
  - SQLAlchemy and psycopg2-binary are installed in the project
  - Dependencies are listed in pyproject.toml
  - Virtual environment is properly configured with new packages

## Task T-002: Create Database Module [x]
- **Description**: Set up the database configuration using SQLAlchemy
- **Steps**:
  - Create src/database.py
  - Set up the engine using DATABASE_URL environment variable
  - Create SessionLocal factory for database sessions
  - Create Base class for ORM models
- **Definition of Done**:
  - Database engine is configured
  - SessionLocal factory is created
  - Base class is created
  - Environment variable is properly used for database connection

## Task T-003: Define ORM Model [x]
- **Description**: Update the Task model to use SQLAlchemy ORM
- **Steps**:
  - Update src/models.py to inherit from Base
  - Map fields to database columns:
    - id: Integer, Primary Key
    - title: String
    - description: String
    - completed: Boolean
  - Maintain backward compatibility where possible
- **Definition of Done**:
  - Task class inherits from SQLAlchemy Base
  - All fields are properly mapped to database columns
  - Primary key is configured
  - Model maintains compatibility with existing code

## Task T-004: Update Service Layer [x]
- **Description**: Update services to use database operations
- **Steps**:
  - Modify service functions to use database sessions
  - Update create_task to store in database
  - Update get_all_tasks to retrieve from database
  - Update other service functions to use database
- **Definition of Done**:
  - All service functions use database operations
  - Database sessions are properly managed
  - All functionality is preserved

## Task T-005: Test Database Integration [x]
- **Description**: Verify the database integration works correctly
- **Steps**:
  - Update existing tests to work with database
  - Run tests to ensure functionality
  - Verify data persistence
- **Definition of Done**:
  - All tests pass with database backend
  - Data is properly persisted in database
  - API functionality is maintained

## Task T-006: Environment Configuration [x]
- **Description**: Set up environment variables and configuration
- **Steps**:
  - Install python-dotenv
  - Create .env file with DATABASE_URL
  - Update database.py to load environment variables
- **Definition of Done**:
  - python-dotenv is installed and used
  - .env file is created with proper configuration
  - Environment variables are properly loaded

## Task T-007: API Integration [x]
- **Description**: Update API endpoints to use database sessions
- **Steps**:
  - Add get_db dependency to src/api.py
  - Update all route functions to accept db: Session = Depends(get_db)
  - Pass database session to service functions
- **Definition of Done**:
  - All API endpoints use database sessions
  - Dependency injection is properly implemented
  - All service calls include database session

## Task T-008: CLI Integration [x]
- **Description**: Update CLI to use database sessions
- **Steps**:
  - Update all CLI handler functions to use database sessions
  - Implement proper session management
- **Definition of Done**:
  - All CLI functions use database sessions
  - Session management is properly implemented
  - CLI functionality is preserved

## Task T-009: Final Testing and Verification [x]
- **Description**: Complete end-to-end testing of database integration
- **Steps**:
  - Run all tests to verify functionality
  - Verify data persistence between application restarts
  - Test both CLI and API functionality
- **Definition of Done**:
  - All tests pass
  - Data persists correctly in database
  - Both CLI and API work with database backend