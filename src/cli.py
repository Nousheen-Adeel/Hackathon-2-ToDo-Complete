"""
CLI interface for the Todo CLI application.

This module contains the command-line interface for interacting with tasks.
"""

from typing import Optional
from src.database import SessionLocal
from src.services import (
    create_task, get_all_tasks, update_task, delete_task,
    toggle_task_completion, get_task_by_id
)


def main_loop():
    """
    Main command loop that displays the menu and handles user input.
    """
    print("Welcome to the Todo CLI Application!")

    while True:
        print("\n" + "="*40)
        print("TODO CLI MENU")
        print("="*40)
        print("1. Add Task")
        print("2. List All Tasks")
        print("3. Update Task")
        print("4. Delete Task")
        print("5. Toggle Task Status")
        print("6. Exit")
        print("-"*40)

        try:
            choice = input("Select an option (1-6): ").strip()

            if choice == "1":
                handle_add_task()
            elif choice == "2":
                handle_list_tasks()
            elif choice == "3":
                handle_update_task()
            elif choice == "4":
                handle_delete_task()
            elif choice == "5":
                handle_toggle_task_status()
            elif choice == "6":
                print("Thank you for using the Todo CLI. Goodbye!")
                break
            else:
                print("Invalid option. Please select a number between 1 and 6.")
        except KeyboardInterrupt:
            print("\n\nOperation cancelled by user. Exiting...")
            break
        except Exception as e:
            print(f"An unexpected error occurred: {e}")


def handle_add_task():
    """
    Handle the Add Task menu option.
    """
    try:
        print("\n--- Add New Task ---")
        title = input("Enter task title: ").strip()

        if not title:
            print("Task title cannot be empty.")
            return

        description = input("Enter task description (optional): ").strip()

        # Create a database session
        db = SessionLocal()
        try:
            task = create_task(db, title, description)
            print(f"Task '{task.title}' added successfully with ID {task.id}!")
        finally:
            db.close()
    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An error occurred while adding the task: {e}")


def handle_list_tasks():
    """
    Handle the List All Tasks menu option.
    """
    try:
        # Create a database session
        db = SessionLocal()
        try:
            tasks = get_all_tasks(db)
        finally:
            db.close()

        if not tasks:
            print("\n--- Your Task List ---")
            print("No tasks found.")
            return

        print("\n--- Your Task List ---")
        print(f"{'ID':<4} {'Status':<10} {'Title':<30}")
        print("-" * 46)

        for task in tasks:
            status = "Completed" if task.completed else "Pending"
            print(f"{task.id:<4} {status:<10} {task.title:<30}")
    except Exception as e:
        print(f"An error occurred while listing tasks: {e}")


def handle_update_task():
    """
    Handle the Update Task menu option.
    """
    try:
        print("\n--- Update Task ---")

        # Create a database session
        db = SessionLocal()
        try:
            if not get_all_tasks(db):
                print("No tasks available to update.")
                return

            task_id_str = input("Enter the task ID to update: ").strip()

            try:
                task_id = int(task_id_str)
            except ValueError:
                print("Invalid task ID. Please enter a number.")
                return

            task = get_task_by_id(db, task_id)
            if not task:
                print(f"Task with ID {task_id} not found.")
                return

            print(f"Current task: {task.title}")
            new_title = input(f"Enter new title (or press Enter to keep '{task.title}'): ").strip()
            new_description = input(f"Enter new description (or press Enter to keep current): ").strip()

            # If the user doesn't want to change a field, pass None to keep it unchanged
            title_to_update = new_title if new_title else None
            description_to_update = new_description if new_description else None

            updated_task = update_task(db, task_id, title_to_update, description_to_update)
        finally:
            db.close()

        if updated_task:
            print(f"Task with ID {task_id} updated successfully!")
        else:
            print(f"Failed to update task with ID {task_id}.")
    except Exception as e:
        print(f"An error occurred while updating the task: {e}")


def handle_delete_task():
    """
    Handle the Delete Task menu option.
    """
    try:
        print("\n--- Delete Task ---")

        # Create a database session
        db = SessionLocal()
        try:
            if not get_all_tasks(db):
                print("No tasks available to delete.")
                return

            task_id_str = input("Enter the task ID to delete: ").strip()

            try:
                task_id = int(task_id_str)
            except ValueError:
                print("Invalid task ID. Please enter a number.")
                return

            task = get_task_by_id(db, task_id)
            if not task:
                print(f"Task with ID {task_id} not found.")
                return

            confirm = input(f"Are you sure you want to delete task '{task.title}'? (y/N): ").strip().lower()

            if confirm in ['y', 'yes']:
                success = delete_task(db, task_id)
                if success:
                    print(f"Task with ID {task_id} deleted successfully!")
                else:
                    print(f"Failed to delete task with ID {task_id}.")
            else:
                print("Task deletion cancelled.")
        finally:
            db.close()
    except Exception as e:
        print(f"An error occurred while deleting the task: {e}")


def handle_toggle_task_status():
    """
    Handle the Toggle Task Status menu option.
    """
    try:
        print("\n--- Toggle Task Status ---")

        # Create a database session
        db = SessionLocal()
        try:
            if not get_all_tasks(db):
                print("No tasks available to toggle.")
                return

            task_id_str = input("Enter the task ID to toggle status: ").strip()

            try:
                task_id = int(task_id_str)
            except ValueError:
                print("Invalid task ID. Please enter a number.")
                return

            task = get_task_by_id(db, task_id)
            if not task:
                print(f"Task with ID {task_id} not found.")
                return

            new_status = "completed" if not task.completed else "pending"
            toggled_task = toggle_task_completion(db, task_id)
        finally:
            db.close()

        if toggled_task:
            print(f"Task '{toggled_task.title}' status changed to {new_status}!")
        else:
            print(f"Failed to toggle status for task with ID {task_id}.")
    except Exception as e:
        print(f"An error occurred while toggling the task status: {e}")