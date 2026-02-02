"""
Entry point for the Todo CLI application.

This module serves as the main entry point for the application.
"""

from src.cli import main_loop
from src.utils import initialize_database


def main():
    """
    Main function that starts the CLI application.
    """
    # Initialize the database
    initialize_database()

    # Start the CLI application
    main_loop()


if __name__ == "__main__":
    main()