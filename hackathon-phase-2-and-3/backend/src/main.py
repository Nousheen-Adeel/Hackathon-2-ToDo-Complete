from fastapi import FastAPI, HTTPException, Body, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import SQLModel, Field, create_engine, Session, select
from typing import List, Optional
import os
import uuid
import hashlib
from datetime import datetime, timedelta
from dotenv import load_dotenv
import google.generativeai as genai
from pydantic import BaseModel, EmailStr
import openai
import jwt

# Load environment variables
load_dotenv()

# JWT Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "fallback-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Security
security = HTTPBearer(auto_error=False)

# Configure OpenAI API (fallback to OpenAI if Gemini is not available)
openai.api_key = os.getenv("OPENAI_API_KEY")

# Gemini API is disabled since we're using OpenAI
GEMINI_AVAILABLE = False
model = None
print("Gemini API disabled, using OpenAI")

# Initialize FastAPI app
app = FastAPI(title="Todo API with JWT Auth")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== MODELS ====================

# User model
class User(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    email: str = Field(unique=True, index=True)
    password_hash: str
    name: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Task model
class TaskBase(SQLModel):
    title: str
    description: Optional[str] = None
    completed: bool = False

class Task(TaskBase, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: Optional[str] = Field(default=None, foreign_key="user.id", index=True)

class TaskCreate(TaskBase):
    pass

class TaskUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None

# ==================== AUTH SCHEMAS ====================

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class UserResponse(BaseModel):
    id: str
    email: str
    name: Optional[str]

# ==================== PASSWORD UTILITIES ====================

def hash_password(password: str) -> str:
    """Hash password using PBKDF2 with SHA-256 and random salt"""
    salt = os.urandom(32)
    key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
    return salt.hex() + ':' + key.hex()

def verify_password(password: str, password_hash: str) -> bool:
    """Verify password against hash"""
    try:
        salt_hex, key_hex = password_hash.split(':')
        salt = bytes.fromhex(salt_hex)
        key = bytes.fromhex(key_hex)
        new_key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
        return key == new_key
    except Exception:
        return False

# ==================== JWT UTILITIES ====================

def create_access_token(user_id: str) -> str:
    """Create access token with 30 minute expiry"""
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": user_id, "exp": expire, "type": "access"}
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

def create_refresh_token(user_id: str) -> str:
    """Create refresh token with 7 day expiry"""
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {"sub": user_id, "exp": expire, "type": "refresh"}
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

def decode_token(token: str) -> Optional[dict]:
    """Decode and validate JWT token"""
    try:
        return jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

# ==================== DATABASE SETUP ====================

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./todo.db")
engine = create_engine(DATABASE_URL, echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(bind=engine)

@app.on_event("startup")
def startup():
    create_db_and_tables()

# ==================== AUTH DEPENDENCIES ====================

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Get current authenticated user from JWT token"""
    if not credentials:
        raise HTTPException(status_code=401, detail="Not authenticated")

    payload = decode_token(credentials.credentials)
    if not payload or payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    with Session(engine) as session:
        user = session.get(User, payload["sub"])
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user

def get_optional_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Optional[User]:
    """Get current user if authenticated, otherwise return None"""
    if not credentials:
        return None
    try:
        return get_current_user(credentials)
    except HTTPException:
        return None

# ==================== AUTH ENDPOINTS ====================

@app.post("/auth/register", response_model=TokenResponse)
def register(user_data: UserCreate):
    """Register a new user"""
    with Session(engine) as session:
        # Check if email exists
        existing = session.exec(select(User).where(User.email == user_data.email)).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")

        # Create user
        user = User(
            email=user_data.email,
            password_hash=hash_password(user_data.password),
            name=user_data.name
        )
        session.add(user)
        session.commit()
        session.refresh(user)

        return TokenResponse(
            access_token=create_access_token(user.id),
            refresh_token=create_refresh_token(user.id)
        )

@app.post("/auth/login", response_model=TokenResponse)
def login(credentials: UserLogin):
    """Login with email and password"""
    with Session(engine) as session:
        user = session.exec(select(User).where(User.email == credentials.email)).first()
        if not user or not verify_password(credentials.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid email or password")

        return TokenResponse(
            access_token=create_access_token(user.id),
            refresh_token=create_refresh_token(user.id)
        )

@app.post("/auth/refresh", response_model=TokenResponse)
def refresh_token(request: RefreshTokenRequest):
    """Refresh access token using refresh token"""
    payload = decode_token(request.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    with Session(engine) as session:
        user = session.get(User, payload["sub"])
        if not user:
            raise HTTPException(status_code=401, detail="User not found")

    return TokenResponse(
        access_token=create_access_token(payload["sub"]),
        refresh_token=create_refresh_token(payload["sub"])
    )

@app.get("/auth/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Get current authenticated user info"""
    return UserResponse(id=current_user.id, email=current_user.email, name=current_user.name)

# ==================== TASK ENDPOINTS (PROTECTED) ====================

@app.get("/")
def read_root():
    return {"Hello": "World", "message": "Todo API with JWT Authentication"}

@app.get("/tasks", response_model=List[Task])
def get_tasks(current_user: User = Depends(get_current_user)):
    """Get all tasks for the current user"""
    with Session(engine) as session:
        tasks = session.exec(select(Task).where(Task.user_id == current_user.id)).all()
        return tasks

@app.post("/tasks", response_model=Task)
def create_task(task: TaskCreate, current_user: User = Depends(get_current_user)):
    """Create a new task for the current user"""
    with Session(engine) as session:
        db_task = Task(
            title=task.title,
            description=task.description,
            completed=task.completed,
            user_id=current_user.id
        )
        session.add(db_task)
        session.commit()
        session.refresh(db_task)
        return db_task

@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: str, current_user: User = Depends(get_current_user)):
    """Get a specific task (must belong to current user)"""
    with Session(engine) as session:
        task = session.exec(
            select(Task).where(Task.id == task_id, Task.user_id == current_user.id)
        ).first()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        return task

@app.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: str, task: TaskUpdate, current_user: User = Depends(get_current_user)):
    """Update a task (must belong to current user)"""
    with Session(engine) as session:
        db_task = session.exec(
            select(Task).where(Task.id == task_id, Task.user_id == current_user.id)
        ).first()
        if not db_task:
            raise HTTPException(status_code=404, detail="Task not found")

        update_data = task.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_task, key, value)

        session.add(db_task)
        session.commit()
        session.refresh(db_task)
        return db_task

@app.delete("/tasks/{task_id}")
def delete_task(task_id: str, current_user: User = Depends(get_current_user)):
    """Delete a task (must belong to current user)"""
    with Session(engine) as session:
        task = session.exec(
            select(Task).where(Task.id == task_id, Task.user_id == current_user.id)
        ).first()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        session.delete(task)
        session.commit()
        return {"message": "Task deleted successfully"}

@app.patch("/tasks/{task_id}/toggle", response_model=Task)
def toggle_task(task_id: str, current_user: User = Depends(get_current_user)):
    """Toggle task completion status (must belong to current user)"""
    with Session(engine) as session:
        task = session.exec(
            select(Task).where(Task.id == task_id, Task.user_id == current_user.id)
        ).first()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        task.completed = not task.completed
        session.add(task)
        session.commit()
        session.refresh(task)
        return task

# ==================== CHAT ENDPOINT (PROTECTED) ====================

class ChatRequest(BaseModel):
    query: str
    tasks: Optional[List[dict]] = []

class ChatResponse(BaseModel):
    response: str

@app.post("/chat", response_model=ChatResponse)
def chat_with_gemini(chat_request: ChatRequest, current_user: User = Depends(get_current_user)):
    """AI chat endpoint with task management (protected)"""
    query = chat_request.query

    # Check if this is the first message (welcome message)
    if query.strip().lower() in ["hello", "hi", "hey", "start", "help", "commands", ""]:
        welcome_message = f"""Welcome {current_user.name or current_user.email}!

**Available Task Commands:**
- **Add Task:** Say "add task [your task description]"
- **Update Task:** Say "update task [current description] to [new description]"
- **Delete Task:** Say "delete task [task description]"
- **List Tasks:** Say "list tasks" or "show tasks"

You can also ask me general questions!

How can I assist you today?"""
        return ChatResponse(response=welcome_message)

    # Check if the query is a task command
    query_lower = query.lower().strip()

    # Handle "add task" command
    if "add task" in query_lower:
        import re
        task_match = re.search(r"add task\s+(.+)", query_lower)
        if task_match:
            task_title = task_match.group(1).strip()

            with Session(engine) as session:
                new_task = Task(title=task_title, description="", completed=False, user_id=current_user.id)
                session.add(new_task)
                session.commit()
                session.refresh(new_task)

            return ChatResponse(response=f"Added task: '{task_title}'")
        else:
            return ChatResponse(response="Please specify a task to add. Format: 'add task <task description>'")

    # Handle "update task" command
    elif "update task" in query_lower and " to " in query_lower:
        import re
        update_match = re.search(r"update task\s+(.+?)\s+to\s+(.+)", query_lower)
        if update_match:
            current_desc = update_match.group(1).strip()
            new_description = update_match.group(2).strip()

            with Session(engine) as session:
                statement = select(Task).where(
                    Task.title.ilike(f"%{current_desc}%"),
                    Task.user_id == current_user.id
                )
                task_to_update = session.exec(statement).first()

                if task_to_update:
                    task_to_update.title = new_description
                    session.add(task_to_update)
                    session.commit()
                    session.refresh(task_to_update)
                    return ChatResponse(response=f"Updated task: '{current_desc}' -> '{new_description}'")
                else:
                    return ChatResponse(response=f"Task with description '{current_desc}' not found")
        else:
            return ChatResponse(response="Please specify current task and new description. Format: 'update task <current description> to <new description>'")

    # Handle "delete task" command
    elif "delete task" in query_lower:
        import re
        delete_match = re.search(r"delete task\s+(.+)", query_lower)
        if delete_match:
            task_desc = delete_match.group(1).strip()

            with Session(engine) as session:
                statement = select(Task).where(
                    Task.title.ilike(f"%{task_desc}%"),
                    Task.user_id == current_user.id
                )
                task_to_delete = session.exec(statement).first()

                if task_to_delete:
                    session.delete(task_to_delete)
                    session.commit()
                    return ChatResponse(response=f"Deleted task: '{task_to_delete.title}'")
                else:
                    return ChatResponse(response=f"Task with description '{task_desc}' not found")
        else:
            return ChatResponse(response="Please specify task to delete. Format: 'delete task <task description>'")

    # Handle "list tasks" command
    elif "list tasks" in query_lower or "show tasks" in query_lower:
        with Session(engine) as session:
            tasks = session.exec(select(Task).where(Task.user_id == current_user.id)).all()

            if not tasks:
                return ChatResponse(response="No tasks found")
            else:
                task_list = "**Your Tasks:**\n"
                for i, task in enumerate(tasks, 1):
                    status = "[Done]" if task.completed else "[Pending]"
                    task_list += f"{i}. {status} {task.title}\n"
                return ChatResponse(response=task_list)

    # Handle legacy task commands
    elif any(keyword in query_lower for keyword in ["add ", "create ", "new ", "make "]) and any(keyword in query_lower for keyword in ["task", "todo", "to do", "mission"]):
        import re
        task_match = re.search(r"(?:add|create|new|make)\s+(?:a\s+)?(?:task|todo|to do|mission)\s+(.+)", query_lower)
        if task_match:
            task_title = task_match.group(1).strip()

            with Session(engine) as session:
                new_task = Task(title=task_title, description="", completed=False, user_id=current_user.id)
                session.add(new_task)
                session.commit()
                session.refresh(new_task)

            return ChatResponse(response=f"Added task: '{task_title}'")
        else:
            return ChatResponse(response="Please specify a task to add. Format: 'add task <task description>'")

    elif any(keyword in query_lower for keyword in ["delete ", "remove "]) and any(keyword in query_lower for keyword in ["task", "todo", "to do", "mission"]):
        import re
        delete_match = re.search(r"(?:delete|remove)\s+(?:a\s+|the\s+)?(?:task|todo|to do|mission)\s+(.+)", query_lower)
        if delete_match:
            task_title = delete_match.group(1).strip()

            with Session(engine) as session:
                statement = select(Task).where(
                    Task.title.ilike(f"%{task_title}%"),
                    Task.user_id == current_user.id
                )
                task_to_delete = session.exec(statement).first()

                if task_to_delete:
                    session.delete(task_to_delete)
                    session.commit()
                    return ChatResponse(response=f"Deleted task: '{task_to_delete.title}'")
                else:
                    return ChatResponse(response=f"I couldn't find a task matching '{task_title}' to delete.")
        else:
            return ChatResponse(response="Please specify a task to delete. Format: 'delete task <id>'")

    elif any(keyword in query_lower for keyword in ["complete ", "finish ", "done ", "mark "]) and any(keyword in query_lower for keyword in ["task", "todo", "to do", "mission"]):
        import re
        complete_match = re.search(r"(?:complete|finish|done|mark)\s+(?:as\s+completed\s+)?(?:a\s+|the\s+)?(?:task|todo|to do|mission)\s+(.+)", query_lower)
        if complete_match:
            task_title = complete_match.group(1).strip()

            with Session(engine) as session:
                statement = select(Task).where(
                    Task.title.ilike(f"%{task_title}%"),
                    Task.user_id == current_user.id
                )
                task_to_update = session.exec(statement).first()

                if task_to_update:
                    task_to_update.completed = True
                    session.add(task_to_update)
                    session.commit()
                    session.refresh(task_to_update)
                    return ChatResponse(response=f"Completed task: '{task_to_update.title}'")
                else:
                    return ChatResponse(response=f"I couldn't find a task matching '{task_title}' to mark as completed.")
        else:
            return ChatResponse(response="I can help you mark tasks as completed. Try saying something like 'complete task <id>' or 'mark task <id> as done'.")

    else:
        # General conversation, send to AI
        with Session(engine) as session:
            user_tasks = session.exec(select(Task).where(Task.user_id == current_user.id)).all()
            task_context = f"\nCurrent tasks: {[task.title for task in user_tasks] if user_tasks else []}"

        prompt = f"""You are a helpful assistant integrated with a task management system.
        The user said: "{query}"
        {task_context}

        Please respond appropriately to the user's request. If they're asking about tasks,
        you can inform them that they can add, delete, or mark tasks as complete using
        natural language commands."""

        try:
            if GEMINI_AVAILABLE and model is not None:
                response = model.generate_content(prompt)
                if response and response.text:
                    return ChatResponse(response=response.text)
                else:
                    return ChatResponse(response="I processed your request but didn't generate a response. Please try again.")
            else:
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key or api_key == "your_openai_api_key_here":
                    return ChatResponse(response="OpenAI API key is not configured. Please set your OpenAI API key in the environment variables.")

                client = openai.OpenAI(api_key=api_key)
                model_name = os.getenv("CHAT_MODEL", "gpt-3.5-turbo")
                response = client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant integrated with a task management system. The user can ask you to manage their tasks using natural language."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=200,
                    temperature=0.7
                )
                return ChatResponse(response=response.choices[0].message.content)
        except openai.AuthenticationError as e:
            print(f"OpenAI Authentication error: {str(e)}")
            return ChatResponse(response="There's an authentication issue with the OpenAI API key. The key may be invalid or expired.")
        except openai.RateLimitError as e:
            print(f"OpenAI Rate Limit error: {str(e)}")
            return ChatResponse(response="You've exceeded the OpenAI rate limit or quota. Please check your OpenAI account usage and billing.")
        except openai.APIConnectionError as e:
            print(f"OpenAI Connection error: {str(e)}")
            return ChatResponse(response="Unable to connect to OpenAI. Please check your internet connection.")
        except openai.PermissionDeniedError as e:
            print(f"OpenAI Permission Denied error: {str(e)}")
            return ChatResponse(response="Permission denied for the OpenAI API. The account may be deactivated or restricted.")
        except openai.APIError as e:
            print(f"OpenAI API error: {str(e)}")
            return ChatResponse(response=f"OpenAI API error: {str(e)}")
        except Exception as e:
            print(f"AI API error: {str(e)}")
            print(f"Query was: {query}")

            if "API_KEY" in str(e).upper() or "AUTH" in str(e).upper():
                return ChatResponse(response="I'm having trouble connecting to the AI service. Please check that the API key is properly configured.")
            elif "quota" in str(e).lower() or "billing" in str(e).lower() or "limit" in str(e).lower():
                return ChatResponse(response="The AI service is currently out of quota or billing is not enabled. Task management functions still work normally.")
            elif "connection" in str(e).lower():
                return ChatResponse(response="I'm having trouble connecting to the AI service. Please check your internet connection.")
            else:
                if len(query.strip()) < 3:
                    return ChatResponse(response="Hi there! I'm your AI assistant. You can ask me to manage your tasks or chat with me about anything!")

                return ChatResponse(response=f"I'm having trouble processing your request right now: '{query[:50]}...', but I can still help you manage your tasks using commands like 'add task', 'complete task', or 'delete task'.")
