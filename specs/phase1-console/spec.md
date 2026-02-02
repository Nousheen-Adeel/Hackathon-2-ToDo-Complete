# Phase 1 Console App Specification

## User Stories for In-Memory Todo CLI

### REQ-001: Add Task
**As a** user,
**I want to** add a task with a title and description,
**so that** I can keep track of things I need to do.

**Acceptance Criteria:**
- System shall allow user to input a task title and description
- System shall assign a unique ID to each new task
- System shall store the task in memory with 'Pending' status by default
- System shall display a confirmation message after successful task creation
- Title field shall be mandatory
- Description field shall be optional

### REQ-002: List Tasks
**As a** user,
**I want to** see all my tasks with their ID, Status (Pending/Completed), and Title,
**so that** I can get an overview of my tasks.

**Acceptance Criteria:**
- System shall display all tasks in a readable format
- Each task shall show its ID, Status, and Title
- If no tasks exist, system shall display an appropriate message
- Completed tasks shall be visually distinguishable from pending tasks
- Tasks shall be listed in the order they were created

### REQ-003: Update Task
**As a** user,
**I want to** edit the title or description of an existing task using its ID,
**so that** I can keep my task information up to date.

**Acceptance Criteria:**
- System shall allow user to specify a task by its ID
- System shall allow editing of the title field
- System shall allow editing of the description field
- System shall update the task in memory
- System shall display a confirmation message after successful update
- System shall show an error if the task ID does not exist

### REQ-004: Delete Task
**As a** user,
**I want to** remove a task from the list using its ID,
**so that** I can remove tasks that are no longer needed.

**Acceptance Criteria:**
- System shall allow user to specify a task by its ID for deletion
- System shall remove the task from memory
- System shall display a confirmation message after successful deletion
- System shall show an error if the task ID does not exist
- The system shall not allow deletion of non-existent tasks

### REQ-005: Toggle Status
**As a** user,
**I want to** mark a task as 'Completed' or 'Pending',
**so that** I can track my progress on tasks.

**Acceptance Criteria:**
- System shall allow user to specify a task by its ID to toggle status
- System shall change the task status from 'Pending' to 'Completed' or vice versa
- System shall update the task in memory with the new status
- System shall display a confirmation message after successful status change
- System shall show an error if the task ID does not exist
- The status shall alternate between 'Pending' and 'Completed' each time it's toggled