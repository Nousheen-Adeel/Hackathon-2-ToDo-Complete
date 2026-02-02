"""
FastAPI application for the Todo API.

This module defines the FastAPI application and its endpoints.
"""
from fastapi import FastAPI, HTTPException, Depends
from typing import List
from pydantic import BaseModel
from src import services
from src.models import Task
from src.database import SessionLocal, Base, engine

# Initialize FastAPI app
app = FastAPI(title="Todo API", description="A simple todo list API", version="1.0.0")

# Create all database tables when the application starts
Base.metadata.create_all(bind=engine)


def get_db():
    """
    Dependency function that provides a database session for each request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class TaskCreate(BaseModel):
    """
    Pydantic model for creating a new task.
    """
    title: str
    description: str = ""


class TaskUpdate(BaseModel):
    """
    Pydantic model for updating a task.
    """
    title: str
    description: str = ""


@app.get("/", status_code=200)
async def root():
    """
    Root endpoint that returns a welcome message.

    Returns:
        dict: A welcome message
    """
    return {"message": "Welcome to the Todo API!"}


@app.get("/tasks", status_code=200, response_model=List[dict])
async def get_tasks(db: SessionLocal = Depends(get_db)):
    """
    Retrieve all tasks from the system.

    Returns:
        List[dict]: A list of all tasks in dictionary format
    """
    tasks = services.get_all_tasks(db)
    # Convert Task objects to dictionaries
    return [task.to_dict() for task in tasks]


@app.post("/tasks", status_code=201, response_model=dict)
async def create_task(task_data: TaskCreate, db: SessionLocal = Depends(get_db)):
    """
    Create a new task.

    Args:
        task_data (TaskCreate): The task data containing title and description
        db: Database session dependency

    Returns:
        dict: The created task with 201 Created status
    """
    task = services.create_task(db, task_data.title, task_data.description)
    return task.to_dict()


@app.put("/tasks/{id}", status_code=200, response_model=dict)
async def update_task(id: int, task_data: TaskUpdate, db: SessionLocal = Depends(get_db)):
    """
    Update an existing task.

    Args:
        id (int): The ID of the task to update
        task_data (TaskUpdate): The updated task data containing title and description
        db: Database session dependency

    Returns:
        dict: The updated task with 200 OK status

    Raises:
        HTTPException: 404 Not Found if the task doesn't exist
    """

    updated_task = services.update_task(db, id, task_data.title, task_data.description)
    if updated_task is None:
        raise HTTPException(status_code=404, detail=f"Task with ID {id} not found")

    return updated_task.to_dict()


@app.delete("/tasks/{id}", status_code=200)
async def delete_task(id: int, db: SessionLocal = Depends(get_db)):
    """
    Delete a task by its ID.

    Args:
        id (int): The ID of the task to delete
        db: Database session dependency

    Returns:
        dict: A success message with 200 OK status

    Raises:
        HTTPException: 404 Not Found if the task doesn't exist
    """

    success = services.delete_task(db, id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Task with ID {id} not found")

    return {"message": f"Task with ID {id} deleted successfully"}


@app.patch("/tasks/{id}/toggle", status_code=200, response_model=dict)
async def toggle_task_status(id: int, db: SessionLocal = Depends(get_db)):
    """
    Toggle the completion status of a task.

    Args:
        id (int): The ID of the task to toggle
        db: Database session dependency

    Returns:
    
        dict: The updated task with 200 OK status

    Raises:
        HTTPException: 404 Not Found if the task doesn't exist
    """

    toggled_task = services.toggle_task_completion(db, id)
    if toggled_task is None:
        raise HTTPException(status_code=404, detail=f"Task with ID {id} not found")

    return toggled_task.to_dict()