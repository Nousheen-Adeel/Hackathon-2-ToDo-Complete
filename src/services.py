"""
Service layer for the Todo CLI application.

This module contains business logic for task management,
using SQLAlchemy ORM for database operations.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from src.models import Task


def create_task(db: Session, title: str, description: str = "") -> Task:
    """
    Create a new task with the provided title and description.

    Args:
        db (Session): Database session
        title (str): The title of the task (must not be empty)
        description (str): The description of the task (optional)

    Returns:
        Task: The created Task object

    Raises:
        ValueError: If the title is empty
        SQLAlchemyError: If there's a database error
    """
    # Validate that the title is not empty
    if not title or title.strip() == "":
        raise ValueError("Task title cannot be empty")

    # Create a new Task instance
    new_task = Task(
        title=title.strip(),
        description=description.strip(),
        completed=False
    )

    try:
        # Add the task to the database
        db.add(new_task)
        db.commit()
        db.refresh(new_task)  # Refresh to get the auto-generated ID
        return new_task
    except SQLAlchemyError as e:
        db.rollback()
        raise e


def get_all_tasks(db: Session) -> List[Task]:
    """
    Retrieve all tasks from the database.

    Args:
        db (Session): Database session

    Returns:
        List[Task]: A list of all Task objects
    """
    try:
        return db.query(Task).all()
    except SQLAlchemyError as e:
        raise e


def get_task_by_id(db: Session, task_id: int) -> Optional[Task]:
    """
    Retrieve a task by its ID from the database.

    Args:
        db (Session): Database session
        task_id (int): The ID of the task to retrieve

    Returns:
        Optional[Task]: The Task object if found, None otherwise
    """
    try:
        return db.query(Task).filter(Task.id == task_id).first()
    except SQLAlchemyError as e:
        raise e


def update_task(db: Session, task_id: int, title: Optional[str] = None, description: Optional[str] = None) -> Optional[Task]:
    """
    Update an existing task's title or description.

    Args:
        db (Session): Database session
        task_id (int): The ID of the task to update
        title (Optional[str]): The new title (if provided)
        description (Optional[str]): The new description (if provided)

    Returns:
        Optional[Task]: The updated Task object if found, None otherwise
    """
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if task is None:
            return None

        if title is not None:
            task.title = title.strip()
        if description is not None:
            task.description = description.strip()

        db.commit()
        db.refresh(task)
        return task
    except SQLAlchemyError as e:
        db.rollback()
        raise e


def delete_task(db: Session, task_id: int) -> bool:
    """
    Delete a task by its ID from the database.

    Args:
        db (Session): Database session
        task_id (int): The ID of the task to delete

    Returns:
        bool: True if the task was deleted, False if it didn't exist
    """
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if task is None:
            return False

        db.delete(task)
        db.commit()
        return True
    except SQLAlchemyError as e:
        db.rollback()
        raise e


def toggle_task_completion(db: Session, task_id: int) -> Optional[Task]:
    """
    Toggle the completion status of a task.

    Args:
        db (Session): Database session
        task_id (int): The ID of the task to toggle

    Returns:
        Optional[Task]: The updated Task object if found, None otherwise
    """
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if task is None:
            return None

        task.completed = not task.completed
        db.commit()
        db.refresh(task)
        return task
    except SQLAlchemyError as e:
        db.rollback()
        raise e