"""
Test suite for the API endpoints.

This module contains tests for all API endpoints using TestClient.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.api import app
from src.database import Base
from src.models import Task


# Create a test database engine and session
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
test_engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture
def client():
    """Create a test client for the API with a clean database for each test."""
    # Create all tables
    Base.metadata.create_all(bind=test_engine)
    
    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()
    
    # Override the get_db dependency in the API
    from src.api import get_db
    app.dependency_overrides[get_db] = override_get_db
    
    # Create test client
    test_client = TestClient(app)
    yield test_client
    
    # Clean up after test
    app.dependency_overrides.clear()


def test_read_root(client):
    """Test the root endpoint returns the welcome message."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Todo API!"}


def test_create_task(client):
    """Test creating a new task returns 201 and correct data."""
    task_data = {
        "title": "Test Task",
        "description": "Test Description"
    }
    response = client.post("/tasks", json=task_data)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Task"
    assert data["description"] == "Test Description"
    assert data["completed"] is False
    assert "id" in data
    assert isinstance(data["id"], int)


def test_get_tasks(client):
    """Test that the task list contains the created task."""
    # First create a task
    task_data = {
        "title": "Get Tasks Test",
        "description": "Test Description"
    }
    create_response = client.post("/tasks", json=task_data)
    assert create_response.status_code == 201
    created_task = create_response.json()

    # Then get all tasks
    response = client.get("/tasks")
    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) >= 1
    # Check that our created task is in the list
    found_task = None
    for task in tasks:
        if task["id"] == created_task["id"]:
            found_task = task
            break
    assert found_task is not None
    assert found_task["title"] == "Get Tasks Test"
    assert found_task["description"] == "Test Description"


def test_update_task(client):
    """Test updating task details changes successfully."""
    # First create a task
    create_data = {
        "title": "Original Title",
        "description": "Original Description"
    }
    create_response = client.post("/tasks", json=create_data)
    assert create_response.status_code == 201
    created_task = create_response.json()

    # Then update the task
    update_data = {
        "title": "Updated Title",
        "description": "Updated Description"
    }
    response = client.put(f"/tasks/{created_task['id']}", json=update_data)
    assert response.status_code == 200
    updated_task = response.json()
    assert updated_task["title"] == "Updated Title"
    assert updated_task["description"] == "Updated Description"
    assert updated_task["id"] == created_task["id"]


def test_toggle_task(client):
    """Test that the completed status flips when toggling."""
    # First create a task (should be incomplete by default)
    task_data = {
        "title": "Toggle Test Task",
        "description": "Test Description"
    }
    create_response = client.post("/tasks", json=task_data)
    assert create_response.status_code == 201
    created_task = create_response.json()
    assert created_task["completed"] is False  # Should be False initially

    # Toggle the task status
    response = client.patch(f"/tasks/{created_task['id']}/toggle")
    assert response.status_code == 200
    toggled_task = response.json()
    assert toggled_task["id"] == created_task["id"]
    assert toggled_task["completed"] is True  # Should be True after first toggle

    # Toggle again to make sure it goes back to False
    response = client.patch(f"/tasks/{created_task['id']}/toggle")
    assert response.status_code == 200
    toggled_again_task = response.json()
    assert toggled_again_task["id"] == created_task["id"]
    assert toggled_again_task["completed"] is False  # Should be False after second toggle


def test_delete_task(client):
    """Test that the task is removed after deletion."""
    # First create a task
    task_data = {
        "title": "Delete Test Task",
        "description": "Test Description"
    }
    create_response = client.post("/tasks", json=task_data)
    assert create_response.status_code == 201
    created_task = create_response.json()

    # Verify the task exists
    get_response = client.get("/tasks")
    assert get_response.status_code == 200
    tasks_before = get_response.json()
    task_ids_before = [task["id"] for task in tasks_before]
    assert created_task["id"] in task_ids_before

    # Delete the task
    response = client.delete(f"/tasks/{created_task['id']}")
    assert response.status_code == 200
    assert response.json() == {"message": f"Task with ID {created_task['id']} deleted successfully"}

    # Verify the task is gone
    get_response = client.get("/tasks")
    assert get_response.status_code == 200
    tasks_after = get_response.json()
    task_ids_after = [task["id"] for task in tasks_after]
    assert created_task["id"] not in task_ids_after


def test_update_nonexistent_task(client):
    """Test updating a non-existent task returns 404."""
    update_data = {
        "title": "Updated Title",
        "description": "Updated Description"
    }
    response = client.put("/tasks/99999", json=update_data)
    assert response.status_code == 404


def test_delete_nonexistent_task(client):
    """Test deleting a non-existent task returns 404."""
    response = client.delete("/tasks/99999")
    assert response.status_code == 404


def test_toggle_nonexistent_task(client):
    """Test toggling a non-existent task returns 404."""
    response = client.patch("/tasks/99999/toggle")
    assert response.status_code == 404