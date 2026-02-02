# Phase 3 Database Integration Specification

## Overview
This specification defines the database integration for the Todo application. We will migrate from in-memory storage to a persistent database using SQLAlchemy ORM while maintaining the same API functionality.

## Requirements

### 1. Database Setup
- Use PostgreSQL as the database backend
- Implement SQLAlchemy ORM for database operations
- Maintain backward compatibility with existing API endpoints
- Use environment variables for database configuration

### 2. Data Model Migration
- Convert the in-memory Task model to a SQLAlchemy ORM model
- Preserve all existing functionality (create, read, update, delete, toggle status)
- Ensure data integrity with proper primary keys and constraints

### 3. Configuration
- Use DATABASE_URL environment variable for database connection
- Support connection pooling
- Implement proper database session management

## Database Schema

### Task Table
- **id**: Integer, Primary Key, Auto-increment
- **title**: String (not null)
- **description**: String (nullable)
- **completed**: Boolean (default: false)

## API Compatibility
All existing API endpoints must continue to work without changes:
- GET /tasks
- POST /tasks
- GET /tasks/{id}
- PUT /tasks/{id}
- DELETE /tasks/{id}
- PATCH /tasks/{id}/toggle

## Migration Strategy
- Preserve existing service layer interface
- Implement database-specific service functions
- Ensure smooth transition from in-memory to database storage
- Maintain data during transition (if applicable)

## Error Handling
- Proper database connection error handling
- Transaction management
- Validation of database operations