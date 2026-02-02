"""
Data models for the Todo CLI application.

This module defines the Task class which represents a single task in the system.
"""
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from typing import Dict, Optional

# Import the Base from database module
from .database import Base


class Task(Base):
    """
    Represents a single task in the todo list as a database model.

    Attributes:
        id (int): Unique identifier for the task (Primary Key)
        title (str): Title of the task
        description (str): Description of the task
        completed (bool): Status of the task, True if completed, False otherwise
    """

    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    completed = Column(Boolean, default=False)

    def __init__(self, title: str, description: str = "", completed: bool = False, task_id: Optional[int] = None):
        """
        Initialize a new Task instance.

        Args:
            title (str): The title of the task
            description (str): The description of the task
            completed (bool): Whether the task is completed
            task_id (Optional[int]): The ID of the task (for existing records)
        """
        self.title = title
        self.description = description
        self.completed = completed
        if task_id is not None:
            self.id = task_id

    def to_dict(self) -> Dict:
        """
        Convert the Task instance to a dictionary representation.

        Returns:
            Dict: A dictionary containing the task's attributes
        """
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "completed": self.completed
        }

    def __repr__(self) -> str:
        """
        Return a string representation of the Task instance.

        Returns:
            str: String representation of the task
        """
        return f"Task(id={self.id}, title='{self.title}', description='{self.description}', completed={self.completed})"