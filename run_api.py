"""
Entry point for the Todo API application.

This module serves as the entry point for running the FastAPI application.
"""
from src.api import app
from src.utils import initialize_database


# Initialize the database when the module is imported
# This ensures the database tables are created when the API starts
initialize_database()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)