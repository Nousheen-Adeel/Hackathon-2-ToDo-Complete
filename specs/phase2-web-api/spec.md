# Phase 2 Web API Specification

## Overview
This specification defines the REST API endpoints for the Todo application. The API will expose the existing functionality through HTTP endpoints while maintaining the in-memory storage approach.

## API Endpoints

### 1. POST /tasks (Add Task)
**Description**: Creates a new task with the provided title and description.

**Request**:
- Method: POST
- Endpoint: `/tasks`
- Content-Type: `application/json`
- Body:
  ```json
  {
    "title": "Task title (required, non-empty)",
    "description": "Task description (optional)"
  }
  ```

**Response**:
- Success: `201 Created`
- Body:
  ```json
  {
    "id": 1,
    "title": "Task title",
    "description": "Task description",
    "completed": false
  }
  ```
- Error: `400 Bad Request` if title is empty

### 2. GET /tasks (List Tasks)
**Description**: Retrieves all tasks from the system.

**Request**:
- Method: GET
- Endpoint: `/tasks`

**Response**:
- Success: `200 OK`
- Body:
  ```json
  [
    {
      "id": 1,
      "title": "Task title",
      "description": "Task description",
      "completed": false
    },
    {
      "id": 2,
      "title": "Another task",
      "description": "Description",
      "completed": true
    }
  ]
  ```

### 3. PUT /tasks/{id} (Update Task)
**Description**: Updates the title and/or description of an existing task.

**Request**:
- Method: PUT
- Endpoint: `/tasks/{id}`
- Content-Type: `application/json`
- Path Parameter: `id` (integer)
- Body:
  ```json
  {
    "title": "Updated task title",
    "description": "Updated task description"
  }
  ```

**Response**:
- Success: `200 OK`
- Body:
  ```json
  {
    "id": 1,
    "title": "Updated task title",
    "description": "Updated task description",
    "completed": false
  }
  ```
- Error: `404 Not Found` if task with given ID doesn't exist

### 4. DELETE /tasks/{id} (Delete Task)
**Description**: Deletes a task by its ID.

**Request**:
- Method: DELETE
- Endpoint: `/tasks/{id}`
- Path Parameter: `id` (integer)

**Response**:
- Success: `200 OK`
- Body:
  ```json
  {
    "message": "Task with ID {id} deleted successfully"
  }
  ```
- Error: `404 Not Found` if task with given ID doesn't exist

### 5. PATCH /tasks/{id}/toggle (Toggle Status)
**Description**: Toggles the completion status of a task.

**Request**:
- Method: PATCH
- Endpoint: `/tasks/{id}/toggle`
- Path Parameter: `id` (integer)

**Response**:
- Success: `200 OK`
- Body:
  ```json
  {
    "id": 1,
    "title": "Task title",
    "description": "Task description",
    "completed": true
  }
  ```
- Error: `404 Not Found` if task with given ID doesn't exist

## Error Handling
- Invalid input: Return `400 Bad Request` with error details
- Resource not found: Return `404 Not Found`
- Server errors: Return `500 Internal Server Error`

## Data Validation
- Task title must not be empty or contain only whitespace
- Task ID must be a valid positive integer
- All endpoints must return appropriate error messages when validation fails