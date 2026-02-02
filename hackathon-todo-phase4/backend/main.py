from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv
import psycopg2

# Load environment variables from .env file
load_dotenv()
from psycopg2.extras import RealDictCursor
import uuid
from datetime import datetime

from auth import (
    UserCreate, UserLogin, UserResponse, TokenResponse,
    init_users_table, create_user, authenticate_user,
    create_access_token, create_refresh_token, get_current_user, get_optional_user,
    decode_token, get_user_by_id
)
from chat_persistence import (
    init_chat_tables, create_conversation, get_conversation,
    get_user_conversations, add_message, get_conversation_messages,
    get_conversation_with_messages, delete_conversation,
    ConversationCreate, ConversationResponse, MessageCreate
)

app = FastAPI(
    title="Todo API with Authentication & Chat Persistence",
    description="Enhanced Todo API with JWT auth, MCP support, and conversation history",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection
def get_db_connection():
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        conn = psycopg2.connect(database_url)
        return conn
    else:
        raise Exception("DATABASE_URL not configured")

# Task model
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    completed: bool = False

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None

class Task(TaskBase):
    id: str
    created_at: datetime
    user_id: Optional[str] = None

# Chat model
class ChatRequest(BaseModel):
    query: str
    tasks: Optional[List[dict]] = []

class ChatResponse(BaseModel):
    response: str

# Create tasks table if it doesn't exist
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create tasks table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id VARCHAR(36) PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            description TEXT,
            completed BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            user_id VARCHAR(36)
        )
    """)

    # Add user_id column if it doesn't exist (for existing tables)
    cursor.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                          WHERE table_name='tasks' AND column_name='user_id') THEN
                ALTER TABLE tasks ADD COLUMN user_id VARCHAR(36);
            END IF;
        END $$;
    """)

    # Add index on user_id for better query performance
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_tasks_user_id ON tasks(user_id)
    """)

    conn.commit()
    cursor.close()

    # Initialize users table
    init_users_table(conn)

    # Initialize chat tables
    init_chat_tables(conn)

    conn.close()

# Initialize database on startup
@app.on_event("startup")
def startup_event():
    init_db()

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy"}

# Test database connection
@app.get("/db-test")
def test_db_connection():
    try:
        conn = get_db_connection()
        if conn:
            conn.close()
            return {"db_status": "connected"}
        else:
            return {"db_status": "not configured"}
    except Exception as e:
        return {"db_status": "error", "message": str(e)}

# ==================== TASK ENDPOINTS (PROTECTED) ====================

# Get all tasks for current user
@app.get("/tasks", response_model=List[Task])
def get_tasks(current_user: dict = Depends(get_current_user)):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Filter by user_id
        cursor.execute(
            "SELECT * FROM tasks WHERE user_id = %s ORDER BY created_at DESC",
            (current_user["user_id"],)
        )
        rows = cursor.fetchall()

        cursor.close()
        conn.close()

        return [dict(row) for row in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Create a new task for current user
@app.post("/tasks", response_model=Task)
def create_task(task: TaskCreate, current_user: dict = Depends(get_current_user)):
    try:
        print(f"Creating task for user: {current_user}")
        print(f"Task data: {task}")

        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        task_id = str(uuid.uuid4())
        now = datetime.now()
        print(f"Task ID: {task_id}, Time: {now}")

        # Include user_id when creating task
        cursor.execute(
            "INSERT INTO tasks (id, title, description, completed, created_at, user_id) VALUES (%s, %s, %s, %s, %s, %s) RETURNING *",
            (task_id, task.title, task.description, task.completed, now, current_user["user_id"])
        )
        new_task = cursor.fetchone()
        print(f"New task from DB: {new_task}")

        conn.commit()
        cursor.close()
        conn.close()

        result = dict(new_task) if new_task else {}
        print(f"Returning: {result}")
        return result
    except Exception as e:
        print(f"ERROR creating task: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# Get a specific task (must belong to current user)
@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: str, current_user: dict = Depends(get_current_user)):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Filter by both task_id and user_id
        cursor.execute(
            "SELECT * FROM tasks WHERE id = %s AND user_id = %s",
            (task_id, current_user["user_id"])
        )
        task = cursor.fetchone()

        cursor.close()
        conn.close()

        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        return dict(task)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Update a task (must belong to current user)
@app.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: str, task_update: TaskUpdate, current_user: dict = Depends(get_current_user)):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Build dynamic update query
        update_fields = []
        values = []

        if task_update.title is not None:
            update_fields.append("title = %s")
            values.append(task_update.title)
        if task_update.description is not None:
            update_fields.append("description = %s")
            values.append(task_update.description)
        if task_update.completed is not None:
            update_fields.append("completed = %s")
            values.append(task_update.completed)

        if not update_fields:
            raise HTTPException(status_code=400, detail="No fields to update")

        # Filter by both task_id and user_id
        update_query = f"UPDATE tasks SET {', '.join(update_fields)} WHERE id = %s AND user_id = %s RETURNING *"
        values.append(task_id)
        values.append(current_user["user_id"])

        cursor.execute(update_query, values)
        updated_task = cursor.fetchone()

        if not updated_task:
            raise HTTPException(status_code=404, detail="Task not found")

        conn.commit()
        cursor.close()
        conn.close()

        return dict(updated_task)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Delete a task (must belong to current user)
@app.delete("/tasks/{task_id}")
def delete_task(task_id: str, current_user: dict = Depends(get_current_user)):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Filter by both task_id and user_id
        cursor.execute(
            "DELETE FROM tasks WHERE id = %s AND user_id = %s",
            (task_id, current_user["user_id"])
        )
        deleted_count = cursor.rowcount

        conn.commit()
        cursor.close()
        conn.close()

        if deleted_count == 0:
            raise HTTPException(status_code=404, detail="Task not found")

        return {"message": f"Task {task_id} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Toggle task completion status (must belong to current user)
@app.patch("/tasks/{task_id}/toggle", response_model=Task)
def toggle_task_completion(task_id: str, current_user: dict = Depends(get_current_user)):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Filter by both task_id and user_id
        cursor.execute(
            "UPDATE tasks SET completed = NOT completed WHERE id = %s AND user_id = %s RETURNING *",
            (task_id, current_user["user_id"])
        )
        updated_task = cursor.fetchone()

        if not updated_task:
            raise HTTPException(status_code=404, detail="Task not found")

        conn.commit()
        cursor.close()
        conn.close()

        return dict(updated_task)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== CHAT ENDPOINT (PROTECTED) ====================

@app.post("/chat", response_model=ChatResponse)
def chat_with_ai(chat_request: ChatRequest, current_user: dict = Depends(get_current_user)):
    query = chat_request.query.lower().strip()
    user_id = current_user["user_id"]

    # Task command detection
    if "add task" in query:
        # Extract task description after "add task"
        import re
        task_match = re.search(r"add task\s+(.+)", query)
        if task_match:
            task_title = task_match.group(1).strip()
            # Create the task with user_id
            try:
                conn = get_db_connection()
                cursor = conn.cursor(cursor_factory=RealDictCursor)

                task_id = str(uuid.uuid4())
                cursor.execute(
                    "INSERT INTO tasks (id, title, description, completed, user_id) VALUES (%s, %s, '', FALSE, %s) RETURNING *",
                    (task_id, task_title, user_id)
                )
                new_task = cursor.fetchone()

                conn.commit()
                cursor.close()
                conn.close()

                return ChatResponse(response=f"Added task: '{task_title}'")
            except Exception as e:
                return ChatResponse(response=f"Error adding task: {str(e)}")
        else:
            return ChatResponse(response="Please specify a task to add. Format: 'add task <task description>'")

    elif "list tasks" in query or "show tasks" in query:
        try:
            conn = get_db_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            # Filter by user_id
            cursor.execute(
                "SELECT * FROM tasks WHERE user_id = %s ORDER BY created_at DESC",
                (user_id,)
            )
            tasks = cursor.fetchall()

            cursor.close()
            conn.close()

            if not tasks:
                return ChatResponse(response="No tasks found")
            else:
                task_list = "**Your Tasks:**\n"
                for i, task in enumerate(tasks, 1):
                    status = "[Done]" if task['completed'] else "[Pending]"
                    task_list += f"{i}. {status} {task['title']}\n"
                return ChatResponse(response=task_list)
        except Exception as e:
            return ChatResponse(response=f"Error retrieving tasks: {str(e)}")

    elif "delete task" in query:
        # Extract task description after "delete task"
        import re
        task_match = re.search(r"delete task\s+(.+)", query)
        if task_match:
            task_desc = task_match.group(1).strip()
            try:
                conn = get_db_connection()
                cursor = conn.cursor(cursor_factory=RealDictCursor)

                # Find and delete the task by description - filter by user_id
                cursor.execute(
                    "SELECT id, title FROM tasks WHERE title ILIKE %s AND user_id = %s",
                    (f'%{task_desc}%', user_id)
                )
                task_to_delete = cursor.fetchone()

                if task_to_delete:
                    cursor.execute("DELETE FROM tasks WHERE id = %s AND user_id = %s", (task_to_delete['id'], user_id))
                    conn.commit()

                    cursor.close()
                    conn.close()

                    return ChatResponse(response=f"Deleted task: '{task_to_delete['title']}'")
                else:
                    cursor.close()
                    conn.close()
                    return ChatResponse(response=f"Task with description '{task_desc}' not found")
            except Exception as e:
                return ChatResponse(response=f"Error deleting task: {str(e)}")
        else:
            return ChatResponse(response="Please specify task to delete. Format: 'delete task <task description>'")

    elif "update task" in query and " to " in query:
        # Extract current description and new description
        import re
        update_match = re.search(r"update task\s+(.+?)\s+to\s+(.+)", query)
        if update_match:
            current_desc = update_match.group(1).strip()
            new_description = update_match.group(2).strip()

            try:
                conn = get_db_connection()
                cursor = conn.cursor(cursor_factory=RealDictCursor)

                # Find and update the task by description - filter by user_id
                cursor.execute(
                    "SELECT id, title FROM tasks WHERE title ILIKE %s AND user_id = %s",
                    (f'%{current_desc}%', user_id)
                )
                task_to_update = cursor.fetchone()

                if task_to_update:
                    cursor.execute(
                        "UPDATE tasks SET title = %s WHERE id = %s AND user_id = %s RETURNING *",
                        (new_description, task_to_update['id'], user_id)
                    )
                    updated_task = cursor.fetchone()

                    conn.commit()
                    cursor.close()
                    conn.close()

                    return ChatResponse(response=f"Updated task: '{current_desc}' -> '{new_description}'")
                else:
                    cursor.close()
                    conn.close()
                    return ChatResponse(response=f"Task with description '{current_desc}' not found")
            except Exception as e:
                return ChatResponse(response=f"Error updating task: {str(e)}")
        else:
            return ChatResponse(response="Please specify current task and new description. Format: 'update task <current description> to <new description>'")

    elif "complete task" in query or "mark task" in query:
        import re
        complete_match = re.search(r"(?:complete|mark)\s+task\s+(.+?)(?:\s+as\s+(?:done|completed))?$", query)
        if complete_match:
            task_desc = complete_match.group(1).strip()
            try:
                conn = get_db_connection()
                cursor = conn.cursor(cursor_factory=RealDictCursor)

                cursor.execute(
                    "SELECT id, title FROM tasks WHERE title ILIKE %s AND user_id = %s",
                    (f'%{task_desc}%', user_id)
                )
                task_to_complete = cursor.fetchone()

                if task_to_complete:
                    cursor.execute(
                        "UPDATE tasks SET completed = TRUE WHERE id = %s AND user_id = %s RETURNING *",
                        (task_to_complete['id'], user_id)
                    )
                    conn.commit()
                    cursor.close()
                    conn.close()
                    return ChatResponse(response=f"Completed task: '{task_to_complete['title']}'")
                else:
                    cursor.close()
                    conn.close()
                    return ChatResponse(response=f"Task with description '{task_desc}' not found")
            except Exception as e:
                return ChatResponse(response=f"Error completing task: {str(e)}")
        else:
            return ChatResponse(response="Please specify task to complete. Format: 'complete task <task description>'")

    else:
        # General conversation
        if query in ["hello", "hi", "hey", "start", "help", "commands"]:
            user_name = current_user.get("email", "there").split("@")[0]
            welcome_message = f"""Welcome {user_name}!

**Available Task Commands:**
- **Add Task:** Say "add task [your task description]"
- **Update Task:** Say "update task [current description] to [new description]"
- **Delete Task:** Say "delete task [task description]"
- **Complete Task:** Say "complete task [task description]"
- **List Tasks:** Say "list tasks" or "show tasks"

How can I assist you today?"""
            return ChatResponse(response=welcome_message)
        else:
            return ChatResponse(response="I'm a task management assistant. You can ask me to add, update, delete, complete, or list tasks. Type 'help' for commands.")

# ==================== AUTHENTICATION ENDPOINTS ====================

@app.post("/auth/register", response_model=TokenResponse)
def register(user_data: UserCreate):
    """Register a new user"""
    try:
        conn = get_db_connection()
        user = create_user(conn, user_data.email, user_data.password, user_data.name)
        conn.close()

        access_token = create_access_token(user["id"], user["email"])
        refresh_token = create_refresh_token(user["id"], user["email"])

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=1800  # 30 minutes
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/auth/login", response_model=TokenResponse)
def login(credentials: UserLogin):
    """Login with email and password"""
    try:
        conn = get_db_connection()
        user = authenticate_user(conn, credentials.email, credentials.password)
        conn.close()

        if not user:
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password"
            )

        access_token = create_access_token(user["id"], user["email"])
        refresh_token = create_refresh_token(user["id"], user["email"])

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=1800
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/auth/refresh", response_model=TokenResponse)
def refresh_token(refresh_token: str):
    """Refresh access token using refresh token"""
    try:
        payload = decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")

        user_id = payload["sub"]
        email = payload["email"]

        new_access_token = create_access_token(user_id, email)
        new_refresh_token = create_refresh_token(user_id, email)

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            expires_in=1800
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    try:
        conn = get_db_connection()
        user = get_user_by_id(conn, current_user["user_id"])
        conn.close()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return UserResponse(**user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== CONVERSATION ENDPOINTS ====================

@app.post("/conversations", response_model=ConversationResponse)
async def create_new_conversation(
    data: ConversationCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new conversation"""
    try:
        conn = get_db_connection()
        user_id = current_user["user_id"]
        conversation = create_conversation(conn, user_id=user_id, title=data.title)
        conn.close()

        return ConversationResponse(**conversation)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/conversations/{conversation_id}")
async def get_conversation_by_id(conversation_id: str, current_user: dict = Depends(get_current_user)):
    """Get a conversation with all messages (must belong to current user)"""
    try:
        conn = get_db_connection()
        result = get_conversation_with_messages(conn, conversation_id)
        conn.close()

        if not result:
            raise HTTPException(status_code=404, detail="Conversation not found")

        # Verify ownership
        if result.get("user_id") != current_user["user_id"]:
            raise HTTPException(status_code=404, detail="Conversation not found")

        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/conversations")
async def list_user_conversations(current_user: dict = Depends(get_current_user)):
    """List all conversations for current user"""
    try:
        conn = get_db_connection()
        conversations = get_user_conversations(conn, current_user["user_id"])
        conn.close()

        return {"conversations": conversations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/conversations/{conversation_id}/messages")
async def add_conversation_message(
    conversation_id: str,
    message: MessageCreate,
    current_user: dict = Depends(get_current_user)
):
    """Add a message to a conversation (must belong to current user)"""
    try:
        conn = get_db_connection()

        # Verify conversation belongs to user
        conv = get_conversation(conn, conversation_id)
        if not conv or conv.get("user_id") != current_user["user_id"]:
            conn.close()
            raise HTTPException(status_code=404, detail="Conversation not found")

        msg = add_message(conn, conversation_id, message.role, message.content)
        conn.close()

        return msg
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/conversations/{conversation_id}/messages")
async def get_messages(
    conversation_id: str,
    limit: int = 50,
    offset: int = 0,
    current_user: dict = Depends(get_current_user)
):
    """Get messages from a conversation (must belong to current user)"""
    try:
        conn = get_db_connection()

        # Verify conversation belongs to user
        conv = get_conversation(conn, conversation_id)
        if not conv or conv.get("user_id") != current_user["user_id"]:
            conn.close()
            raise HTTPException(status_code=404, detail="Conversation not found")

        messages = get_conversation_messages(conn, conversation_id, limit, offset)
        conn.close()

        return {"messages": messages}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/conversations/{conversation_id}")
async def delete_conversation_by_id(conversation_id: str, current_user: dict = Depends(get_current_user)):
    """Delete a conversation (must belong to current user)"""
    try:
        conn = get_db_connection()

        # Verify conversation belongs to user
        conv = get_conversation(conn, conversation_id)
        if not conv or conv.get("user_id") != current_user["user_id"]:
            conn.close()
            raise HTTPException(status_code=404, detail="Conversation not found")

        deleted = delete_conversation(conn, conversation_id)
        conn.close()

        if not deleted:
            raise HTTPException(status_code=404, detail="Conversation not found")

        return {"message": "Conversation deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
