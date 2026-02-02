from fastapi import FastAPI, HTTPException, Body, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import SQLModel, Field, create_engine, Session, select, Relationship
from typing import List, Optional
import os
from dotenv import load_dotenv
import google.generativeai as genai
from pydantic import BaseModel, EmailStr
import openai
import jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext

# Load environment variables
load_dotenv()

# Configure OpenAI API (fallback to OpenAI if Gemini is not available)
openai.api_key = os.getenv("OPENAI_API_KEY")

# Gemini API is disabled since we're using OpenAI
GEMINI_AVAILABLE = False
model = None
print("Gemini API disabled, using OpenAI")

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security
security = HTTPBearer()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

# Initialize FastAPI app
app = FastAPI(title="Todo API with Gemini AI")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# User model
class UserBase(SQLModel):
    email: str = Field(unique=True, index=True)
    name: str

class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str
    tasks: List["Task"] = Relationship(back_populates="user")

class UserCreate(SQLModel):
    email: str
    name: str
    password: str

class UserLogin(SQLModel):
    email: str
    password: str

class UserResponse(SQLModel):
    id: int
    email: str
    name: str

class TokenResponse(SQLModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

# Task model
class TaskBase(SQLModel):
    title: str
    description: Optional[str] = None
    completed: bool = False

class Task(TaskBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    user: Optional[User] = Relationship(back_populates="tasks")

class TaskCreate(TaskBase):
    pass

class TaskUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./todo.db")
engine = create_engine(DATABASE_URL, echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(bind=engine)

@app.on_event("startup")
def startup():
    create_db_and_tables()

# Authentication dependency
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    token = credentials.credentials
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user_id = payload.get("user_id")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    with Session(engine) as session:
        user = session.get(User, user_id)
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return user

# Auth endpoints
@app.post("/auth/register", response_model=TokenResponse)
def register(user_data: UserCreate):
    with Session(engine) as session:
        # Check if user already exists
        existing_user = session.exec(select(User).where(User.email == user_data.email)).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")

        # Create new user
        hashed_password = get_password_hash(user_data.password)
        new_user = User(
            email=user_data.email,
            name=user_data.name,
            hashed_password=hashed_password
        )
        session.add(new_user)
        session.commit()
        session.refresh(new_user)

        # Generate token
        access_token = create_access_token(data={"user_id": new_user.id})

        return TokenResponse(
            access_token=access_token,
            user=UserResponse(id=new_user.id, email=new_user.email, name=new_user.name)
        )

@app.post("/auth/login", response_model=TokenResponse)
def login(credentials: UserLogin):
    with Session(engine) as session:
        user = session.exec(select(User).where(User.email == credentials.email)).first()
        if not user or not verify_password(credentials.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid email or password")

        # Generate token
        access_token = create_access_token(data={"user_id": user.id})

        return TokenResponse(
            access_token=access_token,
            user=UserResponse(id=user.id, email=user.email, name=user.name)
        )

@app.get("/auth/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse(id=current_user.id, email=current_user.email, name=current_user.name)

# Task endpoints
@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/tasks", response_model=List[Task])
def get_tasks(current_user: User = Depends(get_current_user)):
    with Session(engine) as session:
        tasks = session.exec(select(Task).where(Task.user_id == current_user.id)).all()
        return tasks

@app.post("/tasks", response_model=Task)
def create_task(task: TaskCreate, current_user: User = Depends(get_current_user)):
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
def get_task(task_id: int, current_user: User = Depends(get_current_user)):
    with Session(engine) as session:
        task = session.get(Task, task_id)
        if not task or task.user_id != current_user.id:
            raise HTTPException(status_code=404, detail="Task not found")
        return task

@app.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, task: TaskUpdate, current_user: User = Depends(get_current_user)):
    with Session(engine) as session:
        db_task = session.get(Task, task_id)
        if not db_task or db_task.user_id != current_user.id:
            raise HTTPException(status_code=404, detail="Task not found")

        update_data = task.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_task, key, value)

        session.add(db_task)
        session.commit()
        session.refresh(db_task)
        return db_task

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, current_user: User = Depends(get_current_user)):
    with Session(engine) as session:
        task = session.get(Task, task_id)
        if not task or task.user_id != current_user.id:
            raise HTTPException(status_code=404, detail="Task not found")
        session.delete(task)
        session.commit()
        return {"message": "Task deleted successfully"}

@app.patch("/tasks/{task_id}/toggle", response_model=Task)
def toggle_task(task_id: int, current_user: User = Depends(get_current_user)):
    with Session(engine) as session:
        task = session.get(Task, task_id)
        if not task or task.user_id != current_user.id:
            raise HTTPException(status_code=404, detail="Task not found")

        task.completed = not task.completed
        session.add(task)
        session.commit()
        session.refresh(task)
        return task

# NEW: Enhanced Gemini AI chat endpoint
class ChatRequest(BaseModel):
    query: str
    tasks: Optional[List[dict]] = []

class ChatResponse(BaseModel):
    response: str

@app.post("/chat", response_model=ChatResponse)
def chat_with_gemini(chat_request: ChatRequest, current_user: User = Depends(get_current_user)):
    query = chat_request.query
    tasks = chat_request.tasks
    user_id = current_user.id

    # Check if this is the first message (welcome message)
    if query.strip().lower() in ["hello", "hi", "hey", "start", "help", "commands", ""]:
        welcome_message = """✨ **Welcome to the Task Management Chatbot!** ✨

📌 **Available Task Commands:**
🆕 **Add Task:** Say "add task [your task description]"
📝 **Update Task:** Say "update task [current description] to [new description]"
❌ **Delete Task:** Say "delete task [task description]"
📋 **List Tasks:** Say "list tasks" or "show tasks"

💬 You can also ask me general questions and chat with me!

How can I assist you today? 😊"""
        return ChatResponse(response=welcome_message)

    # Check if the query is a task command
    query_lower = query.lower().strip()

    # Task command detection
    # Handle "add task" command
    if "add task" in query_lower:
        import re
        # Extract task description after "add task"
        task_match = re.search(r"add task\s+(.+)", query_lower)
        if task_match:
            task_title = task_match.group(1).strip()

            # Create the task
            with Session(engine) as session:
                new_task = Task(title=task_title, description="", completed=False, user_id=user_id)
                session.add(new_task)
                session.commit()
                session.refresh(new_task)

            return ChatResponse(response=f"✅ Added task: '{task_title}'")
        else:
            return ChatResponse(response="Please specify a task to add. Format: 'add task <task description>'")

    # Handle "update task" command
    elif "update task" in query_lower and " to " in query_lower:
        import re
        # Extract current description and new description
        update_match = re.search(r"update task\s+(.+?)\s+to\s+(.+)", query_lower)
        if update_match:
            current_desc = update_match.group(1).strip()
            new_description = update_match.group(2).strip()

            # Find and update the task by description
            with Session(engine) as session:
                # First, get all tasks to find the one to update (filtered by user)
                statement = select(Task).where(Task.user_id == user_id, Task.title.ilike(f"%{current_desc}%"))
                task_to_update = session.exec(statement).first()

                if task_to_update:
                    task_to_update.title = new_description
                    session.add(task_to_update)
                    session.commit()
                    session.refresh(task_to_update)
                    return ChatResponse(response=f"✏️ Updated task: '{current_desc}' → '{new_description}'")
                else:
                    return ChatResponse(response=f"❌ Task with description '{current_desc}' not found")
        else:
            return ChatResponse(response="Please specify current task and new description. Format: 'update task <current description> to <new description>'")

    # Handle "delete task" command
    elif "delete task" in query_lower:
        import re
        # Extract task description to delete
        delete_match = re.search(r"delete task\s+(.+)", query_lower)
        if delete_match:
            task_desc = delete_match.group(1).strip()

            # Find and delete the task by description
            with Session(engine) as session:
                # First, get all tasks to find the one to delete (filtered by user)
                statement = select(Task).where(Task.user_id == user_id, Task.title.ilike(f"%{task_desc}%"))
                task_to_delete = session.exec(statement).first()

                if task_to_delete:
                    session.delete(task_to_delete)
                    session.commit()
                    return ChatResponse(response=f"🗑️ Deleted task: '{task_to_delete.title}'")
                else:
                    return ChatResponse(response=f"❌ Task with description '{task_desc}' not found")
        else:
            return ChatResponse(response="Please specify task to delete. Format: 'delete task <task description>'")

    # Handle "list tasks" command
    elif "list tasks" in query_lower or "show tasks" in query_lower:
        with Session(engine) as session:
            tasks = session.exec(select(Task).where(Task.user_id == user_id)).all()

            if not tasks:
                return ChatResponse(response="📋 No tasks found")
            else:
                task_list = "📋 **Your Tasks:**\n"
                for i, task in enumerate(tasks, 1):
                    status = "✅" if task.completed else "⏳"
                    task_list += f"{i}. [{status}] **#{task.id}** {task.title}\n"
                return ChatResponse(response=task_list)

    elif any(keyword in query_lower for keyword in ["add ", "create ", "new ", "make "]) and any(keyword in query_lower for keyword in ["task", "todo", "to do", "mission"]):
        # This is likely a task creation command (legacy format)
        import re
        # Look for the task description after keywords
        task_match = re.search(r"(?:add|create|new|make)\s+(?:a\s+)?(?:task|todo|to do|mission)\s+(.+)", query_lower)
        if task_match:
            task_title = task_match.group(1).strip()

            # Create the task
            with Session(engine) as session:
                new_task = Task(title=task_title, description="", completed=False, user_id=user_id)
                session.add(new_task)
                session.commit()
                session.refresh(new_task)

            return ChatResponse(response=f"✅ Added task: '{task_title}'")
        else:
            return ChatResponse(response="Please specify a task to add. Format: 'add task <task description>'")

    elif any(keyword in query_lower for keyword in ["delete ", "remove "]) and any(keyword in query_lower for keyword in ["task", "todo", "to do", "mission"]):
        # Handle task deletion (legacy format)
        import re
        # Look for task title to delete
        delete_match = re.search(r"(?:delete|remove)\s+(?:a\s+|the\s+)?(?:task|todo|to do|mission)\s+(.+)", query_lower)
        if delete_match:
            task_title = delete_match.group(1).strip()

            # Find and delete the task
            with Session(engine) as session:
                # First, get all tasks to find the one to delete
                statement = select(Task).where(Task.title.ilike(f"%{task_title}%"))
                task_to_delete = session.exec(statement).first()

                if task_to_delete:
                    session.delete(task_to_delete)
                    session.commit()
                    return ChatResponse(response=f"🗑️ Deleted task: '{task_to_delete.title}'")
                else:
                    return ChatResponse(response=f"I couldn't find a task matching '{task_title}' to delete.")
        else:
            return ChatResponse(response="Please specify a task to delete. Format: 'delete task <id>'")

    elif any(keyword in query_lower for keyword in ["complete ", "finish ", "done ", "mark "]) and any(keyword in query_lower for keyword in ["task", "todo", "to do", "mission"]):
        # Handle task completion (legacy format)
        import re
        # Look for task title to mark as complete
        complete_match = re.search(r"(?:complete|finish|done|mark)\s+(?:as\s+completed\s+)?(?:a\s+|the\s+)?(?:task|todo|to do|mission)\s+(.+)", query_lower)
        if complete_match:
            task_title = complete_match.group(1).strip()

            # Find and update the task
            with Session(engine) as session:
                # First, get all tasks to find the one to update
                statement = select(Task).where(Task.title.ilike(f"%{task_title}%"))
                task_to_update = session.exec(statement).first()

                if task_to_update:
                    task_to_update.completed = True
                    session.add(task_to_update)
                    session.commit()
                    session.refresh(task_to_update)
                    return ChatResponse(response=f"✅ Completed task: '{task_to_update.title}'")
                else:
                    return ChatResponse(response=f"I couldn't find a task matching '{task_title}' to mark as completed.")
        else:
            return ChatResponse(response="I can help you mark tasks as completed. Try saying something like 'complete task <id>' or 'mark task <id> as done'.")

    else:
        # General conversation, send to Gemini
        task_context = f"\nCurrent tasks: {[task['title'] for task in tasks] if tasks else []}"

        # Create a more detailed prompt for the AI
        prompt = f"""You are a helpful assistant integrated with a task management system.
        The user said: "{query}"
        {task_context}

        Please respond appropriately to the user's request. If they're asking about tasks,
        you can inform them that they can add, delete, or mark tasks as complete using
        natural language commands."""

        try:
            # Try using Gemini API first
            if GEMINI_AVAILABLE and model is not None:
                response = model.generate_content(prompt)
                if response and response.text:
                    return ChatResponse(response=response.text)
                else:
                    return ChatResponse(response="I processed your request but didn't generate a response. Please try again.")
            else:
                # Fallback to OpenAI API
                # Using the newer OpenAI SDK format
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key or api_key == "your_openai_api_key_here":
                    return ChatResponse(response="OpenAI API key is not configured. Please set your OpenAI API key in the environment variables.")

                client = openai.OpenAI(api_key=api_key)
                # Use gpt-4o-mini if specified in environment, otherwise default to gpt-3.5-turbo
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
            # More detailed error handling
            print(f"AI API error: {str(e)}")  # This will help debug
            print(f"Query was: {query}")  # Debug info

            # Check if it's an authentication or configuration issue
            if "API_KEY" in str(e).upper() or "AUTH" in str(e).upper():
                return ChatResponse(response="I'm having trouble connecting to the AI service. Please check that the API key is properly configured.")
            elif "quota" in str(e).lower() or "billing" in str(e).lower() or "limit" in str(e).lower():
                return ChatResponse(response="The AI service is currently out of quota or billing is not enabled. Task management functions still work normally.")
            elif "connection" in str(e).lower():
                return ChatResponse(response="I'm having trouble connecting to the AI service. Please check your internet connection.")
            else:
                # Generic fallback response
                if len(query.strip()) < 3:
                    return ChatResponse(response="Hi there! I'm your AI assistant. You can ask me to manage your tasks or chat with me about anything!")

                # For longer queries, provide a more helpful response
                return ChatResponse(response=f"I'm having trouble processing your request right now: '{query[:50]}...', but I can still help you manage your tasks using commands like 'add task', 'complete task', or 'delete task'.")