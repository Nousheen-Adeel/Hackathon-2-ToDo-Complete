# Phase 1 Console App Implementation Plan

## 1. Modular Architecture

The application will be structured in three separate files to ensure separation of concerns:

- **models.py**: Contains data structures and task representation
  - Defines the Task class with attributes: id, title, description, and status
  - Implements data validation for task properties
  - Includes methods for creating and updating task properties

- **services.py**: Contains business logic for task management
  - Implements functions for adding, listing, updating, deleting, and toggling tasks
  - Manages in-memory storage operations
  - Handles validation and error checking for all operations
  - Ensures task IDs are unique and properly assigned

- **cli.py**: Contains the user interface and command loop
  - Implements the main command loop for user interaction
  - Handles user input parsing and validation
  - Displays formatted output to the user
  - Orchestrates calls to service functions based on user commands

## 2. Data Management

The in-memory storage will be implemented using Python dictionaries:

- A dictionary will store tasks with the task ID as the key and the Task object as the value
- Task IDs will be generated using a simple incremental counter starting from 1
- The data structure will ensure each task has a unique ID
- All data operations will occur in memory without any file I/O or database connections
- The storage will be initialized as empty when the application starts

## 3. CLI Design

The main command loop will follow this interaction pattern:

- Display a menu with options: Add, List, Update, Delete, Toggle Status, and Exit
- Accept numeric input or command keywords to select an action
- Prompt for necessary parameters based on the selected action:
  - Add: Request title and optional description
  - List: No additional input required
  - Update: Request task ID, new title, and/or new description
  - Delete: Request task ID
  - Toggle: Request task ID
- Validate user input and display appropriate error messages
- Return to the main menu after each operation or on error
- Include an option to exit the application

## 4. Verification

Testing will be implemented using pytest to verify each feature:

- **Test models.py**: Unit tests for the Task class and its methods
- **Test services.py**: Unit tests for all service functions (add, list, update, delete, toggle)
- **Test cli.py**: Integration tests for the command loop and user interaction
- **Feature-specific tests**:
  - Add Task: Verify task creation, ID assignment, default status, and validation
  - List Tasks: Verify proper display of all tasks with correct formatting
  - Update Task: Verify title/description updates and error handling for invalid IDs
  - Delete Task: Verify task removal and error handling for invalid IDs
  - Toggle Status: Verify status changes and error handling for invalid IDs
- **Edge case tests**: Empty task list, invalid inputs, non-existent IDs

## 5. Constitution Check

This plan explicitly adheres to our constitution.md rules:

- **Python 3.13**: All code will be written using Python 3.13 syntax and features
- **PEP 8 Compliance**: All code will follow PEP 8 style guidelines
- **In-Memory Only**: The plan specifies using Python dictionaries for storage with no file I/O or database connections
- **No Persistent Storage**: The data exists only in memory during execution and is lost when the program exits