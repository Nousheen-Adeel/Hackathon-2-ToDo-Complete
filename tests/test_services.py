"""
Test suite for the services module.

This module contains unit tests for all service functions.
"""
import pytest
from src.models import Task
from src import services


class TestCreateTask:
    """Test cases for the create_task function."""
    
    def setup_method(self):
        """Reset the in-memory storage before each test."""
        services.tasks_storage.clear()
        services.next_task_id = 1
    
    def test_create_task_success(self):
        """Test creating a task with valid title and description."""
        task = services.create_task("Test Title", "Test Description")
        
        assert isinstance(task, Task)
        assert task.id == 1
        assert task.title == "Test Title"
        assert task.description == "Test Description"
        assert task.completed is False
    
    def test_create_task_without_description(self):
        """Test creating a task with only a title."""
        task = services.create_task("Test Title")
        
        assert isinstance(task, Task)
        assert task.title == "Test Title"
        assert task.description == ""
        assert task.completed is False
    
    def test_create_task_empty_title_error(self):
        """Test that creating a task with an empty title raises ValueError."""
        with pytest.raises(ValueError, match="Task title cannot be empty"):
            services.create_task("")
    
    def test_create_task_whitespace_title_error(self):
        """Test that creating a task with whitespace-only title raises ValueError."""
        with pytest.raises(ValueError, match="Task title cannot be empty"):
            services.create_task("   ")
    
    def test_create_task_id_increment(self):
        """Test that task IDs increment correctly."""
        task1 = services.create_task("Task 1", "Description 1")
        task2 = services.create_task("Task 2", "Description 2")
        task3 = services.create_task("Task 3", "Description 3")
        
        assert task1.id == 1
        assert task2.id == 2
        assert task3.id == 3


class TestGetAllTasks:
    """Test cases for the get_all_tasks function."""
    
    def setup_method(self):
        """Reset the in-memory storage before each test."""
        services.tasks_storage.clear()
        services.next_task_id = 1
    
    def test_get_all_tasks_empty(self):
        """Test getting all tasks when storage is empty."""
        tasks = services.get_all_tasks()
        
        assert tasks == []
        assert len(tasks) == 0
    
    def test_get_all_tasks_with_data(self):
        """Test getting all tasks when storage has data."""
        services.create_task("Task 1", "Description 1")
        services.create_task("Task 2", "Description 2")
        
        tasks = services.get_all_tasks()
        
        assert len(tasks) == 2
        assert isinstance(tasks[0], Task)
        assert isinstance(tasks[1], Task)
        assert tasks[0].title == "Task 1"
        assert tasks[1].title == "Task 2"
    
    def test_get_all_tasks_order(self):
        """Test that tasks are returned in the order they were created."""
        task1 = services.create_task("Task 1", "Description 1")
        task2 = services.create_task("Task 2", "Description 2")
        task3 = services.create_task("Task 3", "Description 3")
        
        tasks = services.get_all_tasks()
        
        assert tasks[0].id == task1.id
        assert tasks[1].id == task2.id
        assert tasks[2].id == task3.id


class TestUpdateTask:
    """Test cases for the update_task function."""
    
    def setup_method(self):
        """Reset the in-memory storage before each test."""
        services.tasks_storage.clear()
        services.next_task_id = 1
    
    def test_update_task_title(self):
        """Test updating a task's title."""
        original_task = services.create_task("Original Title", "Original Description")
        updated_task = services.update_task(original_task.id, "New Title")
        
        assert updated_task is not None
        assert updated_task.title == "New Title"
        assert updated_task.description == "Original Description"
    
    def test_update_task_description(self):
        """Test updating a task's description."""
        original_task = services.create_task("Original Title", "Original Description")
        updated_task = services.update_task(original_task.id, description="New Description")
        
        assert updated_task is not None
        assert updated_task.title == "Original Title"
        assert updated_task.description == "New Description"
    
    def test_update_task_both_fields(self):
        """Test updating both title and description."""
        original_task = services.create_task("Original Title", "Original Description")
        updated_task = services.update_task(original_task.id, "New Title", "New Description")
        
        assert updated_task is not None
        assert updated_task.title == "New Title"
        assert updated_task.description == "New Description"
    
    def test_update_task_partial_fields(self):
        """Test updating only one field while keeping the other."""
        original_task = services.create_task("Original Title", "Original Description")
        updated_task = services.update_task(original_task.id, title="New Title")
        
        assert updated_task is not None
        assert updated_task.title == "New Title"
        assert updated_task.description == "Original Description"
    
    def test_update_task_nonexistent_id(self):
        """Test updating a task with a non-existent ID."""
        result = services.update_task(999, "New Title")
        
        assert result is None
    
    def test_update_task_empty_title(self):
        """Test updating a task's title to an empty string."""
        original_task = services.create_task("Original Title", "Original Description")
        updated_task = services.update_task(original_task.id, "")
        
        assert updated_task is not None
        assert updated_task.title == ""


class TestDeleteTask:
    """Test cases for the delete_task function."""
    
    def setup_method(self):
        """Reset the in-memory storage before each test."""
        services.tasks_storage.clear()
        services.next_task_id = 1
    
    def test_delete_task_success(self):
        """Test successfully deleting a task."""
        task = services.create_task("Task to Delete", "Description")
        initial_tasks = services.get_all_tasks()
        
        assert len(initial_tasks) == 1
        
        result = services.delete_task(task.id)
        
        assert result is True
        remaining_tasks = services.get_all_tasks()
        assert len(remaining_tasks) == 0
    
    def test_delete_task_nonexistent_id(self):
        """Test deleting a task with a non-existent ID."""
        result = services.delete_task(999)
        
        assert result is False
    
    def test_delete_task_multiple_tasks(self):
        """Test deleting one task doesn't affect others."""
        task1 = services.create_task("Task 1", "Description 1")
        task2 = services.create_task("Task 2", "Description 2")
        task3 = services.create_task("Task 3", "Description 3")
        
        result = services.delete_task(task2.id)
        
        assert result is True
        remaining_tasks = services.get_all_tasks()
        assert len(remaining_tasks) == 2
        assert not any(t.id == task2.id for t in remaining_tasks)


class TestToggleTaskCompletion:
    """Test cases for the toggle_task_completion function."""
    
    def setup_method(self):
        """Reset the in-memory storage before each test."""
        services.tasks_storage.clear()
        services.next_task_id = 1
    
    def test_toggle_task_completion_from_false_to_true(self):
        """Test toggling a task from pending to completed."""
        task = services.create_task("Test Task", "Description")
        assert task.completed is False
        
        toggled_task = services.toggle_task_completion(task.id)
        
        assert toggled_task is not None
        assert toggled_task.completed is True
    
    def test_toggle_task_completion_from_true_to_false(self):
        """Test toggling a task from completed to pending."""
        task = services.create_task("Test Task", "Description")
        # First toggle to make it completed
        task = services.toggle_task_completion(task.id)
        assert task.completed is True
        
        toggled_task = services.toggle_task_completion(task.id)
        
        assert toggled_task is not None
        assert toggled_task.completed is False
    
    def test_toggle_task_completion_nonexistent_id(self):
        """Test toggling a task with a non-existent ID."""
        result = services.toggle_task_completion(999)
        
        assert result is None
    
    def test_toggle_task_completion_multiple_toggles(self):
        """Test toggling a task multiple times."""
        task = services.create_task("Test Task", "Description")
        assert task.completed is False  # Initially False
        
        # Toggle 1: False -> True
        task = services.toggle_task_completion(task.id)
        assert task.completed is True
        
        # Toggle 2: True -> False
        task = services.toggle_task_completion(task.id)
        assert task.completed is False
        
        # Toggle 3: False -> True
        task = services.toggle_task_completion(task.id)
        assert task.completed is True


class TestGetTaskById:
    """Test cases for the get_task_by_id function."""
    
    def setup_method(self):
        """Reset the in-memory storage before each test."""
        services.tasks_storage.clear()
        services.next_task_id = 1
    
    def test_get_task_by_id_exists(self):
        """Test getting a task that exists."""
        original_task = services.create_task("Test Task", "Description")
        
        retrieved_task = services.get_task_by_id(original_task.id)
        
        assert retrieved_task is not None
        assert retrieved_task.id == original_task.id
        assert retrieved_task.title == original_task.title
        assert retrieved_task.description == original_task.description
        assert retrieved_task.completed == original_task.completed
    
    def test_get_task_by_id_not_exists(self):
        """Test getting a task that doesn't exist."""
        result = services.get_task_by_id(999)
        
        assert result is None