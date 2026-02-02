"""
Utility functions for the Todo CLI application.

This module contains utility functions for database initialization and other common tasks.
"""
from .database import engine, Base


def initialize_database():
    """
    Initialize the database by creating all tables defined in the models.
    This function should be called when the application starts.
    """
    print("Initializing database...")
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully!")


def create_tables():
    """
    Create all database tables defined in the models.
    This is an alias for initialize_database for consistency.
    """
    initialize_database()