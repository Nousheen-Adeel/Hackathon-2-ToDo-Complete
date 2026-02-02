# Phase 3 Database Integration Implementation Plan

## Overview
This plan outlines how we will integrate a database into our existing Todo application using SQLAlchemy ORM. We will maintain the same API functionality while migrating from in-memory storage to persistent storage.

## Architecture Approach
- **SQLAlchemy ORM**: Use SQLAlchemy as the ORM for database operations
- **PostgreSQL**: Use PostgreSQL as the database backend
- **Environment Variables**: Use DATABASE_URL for database configuration
- **Session Management**: Implement proper SQLAlchemy session management
- **Backward Compatibility**: Maintain existing API endpoints and service layer interface

## Implementation Steps

### 1. Dependencies Setup
- Install SQLAlchemy and psycopg2-binary using `uv add sqlalchemy psycopg2-binary`
- Update pyproject.toml with new dependencies

### 2. Database Configuration
- Create `src/database.py` with:
  - Database engine initialization
  - SessionLocal factory
  - Base class for ORM models
  - DATABASE_URL environment variable usage

### 3. ORM Model Definition
- Update `src/models.py` to inherit from SQLAlchemy Base
- Map fields to database columns
- Maintain backward compatibility with existing functionality

### 4. Service Layer Migration
- Update `src/services.py` to use database operations
- Implement database session management
- Preserve existing function signatures and behavior

### 5. Testing
- Update tests to work with database backend
- Implement proper test database configuration
- Ensure all tests pass with database integration

## Technical Details

### Database Structure
```
src/
├── database.py      # (new) SQLAlchemy configuration
├── models.py        # (updated) ORM model
├── services.py      # (updated) Database service functions
├── api.py           # (unchanged) FastAPI endpoints
└── cli.py           # (unchanged) CLI interface
```

### SQLAlchemy Components
- **Engine**: Database connection engine
- **SessionLocal**: Factory for creating database sessions
- **Base**: Base class for ORM models
- **ORM Models**: Database table representations

### Environment Configuration
- DATABASE_URL: Connection string for the database
- Default to a local PostgreSQL instance during development

## Migration Strategy
1. Implement database configuration
2. Create ORM model
3. Update service layer to use database
4. Test functionality with database backend
5. Ensure API compatibility

## Constitution Compliance
- Python 3.13: Continue using Python 3.13
- PEP 8: Follow Python style guidelines
- Database Integration: Transition from in-memory to persistent storage while maintaining functionality