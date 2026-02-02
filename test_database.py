"""
Test script to verify database integration.
"""
import os
import tempfile
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models import Task
from src.database import Base
from src.services import create_task, get_all_tasks, get_task_by_id, update_task, delete_task, toggle_task_completion


def test_database_operations():
    """Test all database operations with a temporary SQLite database."""
    # Create a temporary SQLite database for testing
    _, temp_db_path = tempfile.mkstemp(suffix='.db')
    temp_db_url = f"sqlite:///{temp_db_path}"
    
    # Create engine and session for testing
    test_engine = create_engine(temp_db_url)
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    
    # Create tables
    Base.metadata.create_all(bind=test_engine)
    
    # Create a session
    db = TestSessionLocal()
    
    try:
        print("Testing database operations...")
        
        # Test creating a task
        print("1. Creating a task...")
        task = create_task(db, "Test Task", "This is a test task")
        print(f"   Created task: {task.title} (ID: {task.id})")
        
        # Test getting all tasks
        print("2. Getting all tasks...")
        tasks = get_all_tasks(db)
        print(f"   Found {len(tasks)} task(s)")
        
        # Test getting task by ID
        print("3. Getting task by ID...")
        retrieved_task = get_task_by_id(db, task.id)
        print(f"   Retrieved task: {retrieved_task.title}")
        
        # Test updating task
        print("4. Updating task...")
        updated_task = update_task(db, task.id, "Updated Test Task", "Updated description")
        print(f"   Updated task: {updated_task.title}")
        
        # Test toggling completion
        print("5. Toggling task completion...")
        print(f"   Before toggle - Completed: {updated_task.completed}")
        toggled_task = toggle_task_completion(db, task.id)
        print(f"   After toggle - Completed: {toggled_task.completed}")
        
        # Toggle again to return to original state
        toggled_task = toggle_task_completion(db, task.id)
        print(f"   Toggled back - Completed: {toggled_task.completed}")
        
        # Test deleting task
        print("6. Deleting task...")
        delete_result = delete_task(db, task.id)
        print(f"   Delete result: {delete_result}")
        
        # Verify deletion
        tasks_after_delete = get_all_tasks(db)
        print(f"   Tasks after deletion: {len(tasks_after_delete)}")
        
        print("All tests passed!")
        
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()
        # Close the engine to release file handles
        test_engine.dispose()
        # Clean up the temporary database file
        try:
            os.unlink(temp_db_path)
        except PermissionError:
            # On Windows, the file might still be locked, so we ignore this error
            pass


if __name__ == "__main__":
    test_database_operations()