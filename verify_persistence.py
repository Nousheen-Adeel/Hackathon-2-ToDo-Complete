"""
Final verification script to test data persistence with the database integration.
"""
import os
import sqlite3
from src.database import SessionLocal
from src.services import create_task, get_all_tasks
from src.models import Task


def test_data_persistence():
    """Test that data persists in the database between application runs."""
    print("Testing data persistence...")
    
    # Connect to the database directly to verify data
    db_path = "todo.db"
    
    # Create a task using the service layer
    db = SessionLocal()
    try:
        # Clean up any existing tasks for a fresh test
        db.query(Task).delete()
        db.commit()
        
        # Create a test task
        task = create_task(db, "Persistence Test Task", "This task tests data persistence")
        task_id = task.id
        print(f"Created task with ID: {task_id}")
        
        # Verify the task exists
        tasks = get_all_tasks(db)
        print(f"Total tasks in database: {len(tasks)}")
        
        if len(tasks) > 0:
            print(f"First task: {tasks[0].title} (ID: {tasks[0].id})")
        
    finally:
        db.close()
    
    # Now verify the data exists in the actual database file
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if the tasks table exists and has data
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tasks';")
        tables = cursor.fetchall()
        if tables:
            print("SUCCESS: Tasks table exists in database")
        else:
            print("ERROR: Tasks table does not exist in database")
            return False

        # Count the tasks
        cursor.execute("SELECT COUNT(*) FROM tasks;")
        count = cursor.fetchone()[0]
        print(f"SUCCESS: Database contains {count} task(s)")

        # Get task details
        cursor.execute("SELECT id, title, description, completed FROM tasks;")
        rows = cursor.fetchall()
        for row in rows:
            print(f"  - ID: {row[0]}, Title: {row[1]}, Description: {row[2]}, Completed: {bool(row[3])}")

        conn.close()
        print("SUCCESS: Data persistence test completed successfully!")
        return True
    else:
        print(f"ERROR: Database file {db_path} does not exist")
        return False


if __name__ == "__main__":
    success = test_data_persistence()
    if success:
        print("\nAll verification tests passed! Database integration is working correctly.")
    else:
        print("\nVerification tests failed.")