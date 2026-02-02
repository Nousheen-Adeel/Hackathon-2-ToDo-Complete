# Phase 1 Console App Tasks

## Phase 1: Setup

### TASK-001: Initialize Project [x]
- **Description**: Set up the Python project structure
- **Steps**:
  - Run `uv init` to initialize the project
  - Create the basic directory structure as per constitution
  - Set up Python 3.13 environment
- **Definition of Done**:
  - Project is initialized with proper pyproject.toml
  - Python 3.13 is specified in project configuration
  - Basic project files are created

### TASK-002: Create Models Module [x]
- **Description**: Create the models.py file with Task data structure
- **Steps**:
  - Create src/models.py file
  - Define the Task class with id, title, description, and status attributes
  - Implement data validation for task properties
  - Include methods for creating and updating task properties
- **Definition of Done**:
  - Task class is properly defined
  - All required attributes are included
  - Validation methods are implemented
  - File follows PEP 8 guidelines

### TASK-003: Create Services Module [x]
- **Description**: Create the services.py file with business logic
- **Steps**:
  - Create src/services.py file
  - Implement in-memory storage using dictionary
  - Create function to initialize empty task storage
- **Definition of Done**:
  - Storage mechanism is implemented
  - Dictionary structure is defined
  - Initialization function works properly

### TASK-004: Create CLI Module [x]
- **Description**: Create the cli.py file with user interface
- **Steps**:
  - Create src/cli.py file
  - Implement basic command loop structure
  - Create menu display function
- **Definition of Done**:
  - Basic CLI structure is in place
  - Command loop skeleton exists
  - Menu display function works

### TASK-005: Prompt History Record (PHR) - Setup Phase [x]
- **Description**: Document all prompts and decisions from the setup phase
- **Steps**:
  - Record all prompts given and responses received during setup
  - Store in history/prompts/ directory
  - Include timestamp and description of each prompt
- **Definition of Done**:
  - All setup phase prompts are documented
  - Files are properly stored in history/prompts/
  - Each prompt is timestamped and described

## Phase 2: REQ-001 - Add Task

### TASK-006: Implement Task Creation Logic [x]
- **Description**: Implement the function to create a new task
- **Steps**:
  - Add add_task() function to services.py
  - Generate unique ID for each new task
  - Set default status to 'Pending'
  - Add input validation for title (mandatory)
- **Definition of Done**:
  - Function creates Task objects properly
  - Unique IDs are assigned correctly
  - Default status is set to 'Pending'
  - Title validation works (rejects empty titles)

### TASK-007: Implement CLI Add Task Interface [x]
- **Description**: Implement the CLI interface for adding tasks
- **Steps**:
  - Add option to main menu for adding tasks
  - Implement input prompts for title and description
  - Call service function to create task
  - Display confirmation message
- **Definition of Done**:
  - Menu option exists and works
  - Input prompts work correctly
  - Service function is called properly
  - Confirmation message is displayed

### TASK-008: Test Add Task Feature [x]
- **Description**: Create tests for the add task functionality
- **Steps**:
  - Write unit tests for add_task() function
  - Test successful task creation
  - Test validation (empty title rejection)
  - Test unique ID assignment
- **Definition of Done**:
  - All test cases pass
  - Edge cases are covered
  - Test coverage is adequate

### TASK-009: Prompt History Record (PHR) - Add Task Implementation [x]
- **Description**: Document all prompts and decisions from the Add Task implementation
- **Steps**:
  - Record all prompts given and responses received during Add Task implementation
  - Store in history/prompts/ directory
  - Include timestamp and description of each prompt
- **Definition of Done**:
  - All Add Task implementation prompts are documented
  - Files are properly stored in history/prompts/
  - Each prompt is timestamped and described

## Phase 3: REQ-002 - List Tasks

### TASK-010: Implement Task Listing Logic [x]
- **Description**: Implement the function to list all tasks
- **Steps**:
  - Add list_tasks() function to services.py
  - Return all tasks in creation order
  - Format tasks for display
- **Definition of Done**:
  - Function returns all tasks correctly
  - Tasks are in proper order
  - Format is appropriate for display

### TASK-011: Implement CLI List Tasks Interface [x]
- **Description**: Implement the CLI interface for listing tasks
- **Steps**:
  - Add option to main menu for listing tasks
  - Call service function to get tasks
  - Format and display tasks with ID, Status, and Title
  - Handle case when no tasks exist
- **Definition of Done**:
  - Menu option exists and works
  - Tasks are displayed with required information
  - Empty list case is handled properly
  - Formatting is clear and readable

### TASK-012: Test List Tasks Feature [x]
- **Description**: Create tests for the list tasks functionality
- **Steps**:
  - Write unit tests for list_tasks() function
  - Test listing with multiple tasks
  - Test listing with empty task list
  - Test proper ordering of tasks
- **Definition of Done**:
  - All test cases pass
  - Edge cases are covered
  - Test coverage is adequate

### TASK-013: Prompt History Record (PHR) - List Tasks Implementation [x]
- **Description**: Document all prompts and decisions from the List Tasks implementation
- **Steps**:
  - Record all prompts given and responses received during List Tasks implementation
  - Store in history/prompts/ directory
  - Include timestamp and description of each prompt
- **Definition of Done**:
  - All List Tasks implementation prompts are documented
  - Files are properly stored in history/prompts/
  - Each prompt is timestamped and described

## Phase 4: REQ-003 - Update Task

### TASK-014: Implement Task Update Logic [x]
- **Description**: Implement the function to update an existing task
- **Steps**:
  - Add update_task() function to services.py
  - Find task by ID
  - Update title and/or description
  - Handle error when task ID doesn't exist
- **Definition of Done**:
  - Function updates tasks properly
  - Both title and description can be updated
  - Error handling for invalid IDs works
  - Original task is modified in storage

### TASK-015: Implement CLI Update Task Interface [x]
- **Description**: Implement the CLI interface for updating tasks
- **Steps**:
  - Add option to main menu for updating tasks
  - Prompt for task ID
  - Prompt for new title and/or description
  - Call service function to update task
  - Display confirmation or error message
- **Definition of Done**:
  - Menu option exists and works
  - Input prompts work correctly
  - Service function is called properly
  - Confirmation/error messages are displayed

### TASK-016: Test Update Task Feature [x]
- **Description**: Create tests for the update task functionality
- **Steps**:
  - Write unit tests for update_task() function
  - Test successful task updates
  - Test error handling for invalid IDs
  - Test partial updates (title only, description only)
- **Definition of Done**:
  - All test cases pass
  - Edge cases are covered
  - Test coverage is adequate

### TASK-017: Prompt History Record (PHR) - Update Task Implementation [x]
- **Description**: Document all prompts and decisions from the Update Task implementation
- **Steps**:
  - Record all prompts given and responses received during Update Task implementation
  - Store in history/prompts/ directory
  - Include timestamp and description of each prompt
- **Definition of Done**:
  - All Update Task implementation prompts are documented
  - Files are properly stored in history/prompts/
  - Each prompt is timestamped and described

## Phase 5: REQ-004 - Delete Task

### TASK-018: Implement Task Delete Logic [x]
- **Description**: Implement the function to delete a task
- **Steps**:
  - Add delete_task() function to services.py
  - Find and remove task by ID
  - Handle error when task ID doesn't exist
- **Definition of Done**:
  - Function removes tasks properly
  - Task is removed from storage
  - Error handling for invalid IDs works
  - Function returns appropriate status

### TASK-019: Implement CLI Delete Task Interface [x]
- **Description**: Implement the CLI interface for deleting tasks
- **Steps**:
  - Add option to main menu for deleting tasks
  - Prompt for task ID
  - Call service function to delete task
  - Display confirmation or error message
- **Definition of Done**:
  - Menu option exists and works
  - Input prompts work correctly
  - Service function is called properly
  - Confirmation/error messages are displayed

### TASK-020: Test Delete Task Feature [x]
- **Description**: Create tests for the delete task functionality
- **Steps**:
  - Write unit tests for delete_task() function
  - Test successful task deletion
  - Test error handling for invalid IDs
  - Test that deleted task is no longer in storage
- **Definition of Done**:
  - All test cases pass
  - Edge cases are covered
  - Test coverage is adequate

### TASK-021: Prompt History Record (PHR) - Delete Task Implementation [x]
- **Description**: Document all prompts and decisions from the Delete Task implementation
- **Steps**:
  - Record all prompts given and responses received during Delete Task implementation
  - Store in history/prompts/ directory
  - Include timestamp and description of each prompt
- **Definition of Done**:
  - All Delete Task implementation prompts are documented
  - Files are properly stored in history/prompts/
  - Each prompt is timestamped and described

## Phase 6: REQ-005 - Toggle Status

### TASK-022: Implement Task Toggle Status Logic [x]
- **Description**: Implement the function to toggle task status
- **Steps**:
  - Add toggle_task_status() function to services.py
  - Find task by ID
  - Toggle status between 'Pending' and 'Completed'
  - Handle error when task ID doesn't exist
- **Definition of Done**:
  - Function toggles status properly
  - Status alternates between 'Pending' and 'Completed'
  - Error handling for invalid IDs works
  - Original task is modified in storage

### TASK-023: Implement CLI Toggle Status Interface [x]
- **Description**: Implement the CLI interface for toggling task status
- **Steps**:
  - Add option to main menu for toggling task status
  - Prompt for task ID
  - Call service function to toggle status
  - Display confirmation or error message
- **Definition of Done**:
  - Menu option exists and works
  - Input prompts work correctly
  - Service function is called properly
  - Confirmation/error messages are displayed

### TASK-024: Test Toggle Status Feature [x]
- **Description**: Create tests for the toggle status functionality
- **Steps**:
  - Write unit tests for toggle_task_status() function
  - Test successful status toggling
  - Test error handling for invalid IDs
  - Test alternating between 'Pending' and 'Completed'
- **Definition of Done**:
  - All test cases pass
  - Edge cases are covered
  - Test coverage is adequate

### TASK-025: Prompt History Record (PHR) - Toggle Status Implementation [x]
- **Description**: Document all prompts and decisions from the Toggle Status implementation
- **Steps**:
  - Record all prompts given and responses received during Toggle Status implementation
  - Store in history/prompts/ directory
  - Include timestamp and description of each prompt
- **Definition of Done**:
  - All Toggle Status implementation prompts are documented
  - Files are properly stored in history/prompts/
  - Each prompt is timestamped and described

## Phase 7: Integration and Testing

### TASK-026: Integrate All Components [x]
- **Description**: Ensure all modules work together properly
- **Steps**:
  - Connect CLI functions to service functions
  - Test end-to-end workflow
  - Debug any integration issues
- **Definition of Done**:
  - All features work together
  - No integration errors exist
  - Complete workflow functions properly

### TASK-027: Full System Testing [x]
- **Description**: Test the complete application
- **Steps**:
  - Execute all user stories end-to-end
  - Test error conditions
  - Verify all acceptance criteria are met
- **Definition of Done**:
  - All user stories work as specified
  - Error conditions are handled properly
  - All acceptance criteria are satisfied

### TASK-028: Final Prompt History Record (PHR) [x]
- **Description**: Document all prompts and decisions from the final integration and testing
- **Steps**:
  - Record all prompts given and responses received during final phase
  - Store in history/prompts/ directory
  - Include timestamp and description of each prompt
- **Definition of Done**:
  - All final phase prompts are documented
  - Files are properly stored in history/prompts/
  - Each prompt is timestamped and described