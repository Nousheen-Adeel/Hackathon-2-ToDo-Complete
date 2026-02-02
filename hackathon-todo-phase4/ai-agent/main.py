"""
AI Agent with MCP Support, Skills, and Sub-Agents
Enhanced with database-persisted conversations
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Any, Dict
import os
import httpx

from mcp_sdk import mcp_server, MCPToolResult, MCPContext
from skills import skill_registry, SkillInput
from subagents import orchestrator, SubAgentRequest

app = FastAPI(
    title="AI Agent with MCP, Skills & Sub-Agents",
    description="Enhanced AI Agent with MCP SDK, modular skills, and sub-agent architecture",
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

# Configuration
BACKEND_URL = os.getenv("TODO_BACKEND_URL", "http://todo-backend:8000")


# Models
class Task(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    completed: bool = False


class ChatRequest(BaseModel):
    query: str
    conversation_id: Optional[str] = None
    user_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = {}


class ChatResponse(BaseModel):
    response: str
    conversation_id: Optional[str] = None
    suggestions: List[str] = []
    agent_used: Optional[str] = None


class MCPToolCallRequest(BaseModel):
    tool: str
    arguments: Dict[str, Any] = {}


# Register MCP Tools
@mcp_server.tool(
    name="get_tasks",
    description="Retrieve all tasks from the todo list",
    parameters=[]
)
async def mcp_get_tasks() -> List[dict]:
    """MCP Tool: Get all tasks"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BACKEND_URL}/tasks", timeout=10.0)
        return response.json()


@mcp_server.tool(
    name="create_task",
    description="Create a new task",
    parameters=[
        {"name": "title", "type": "string", "description": "Task title", "required": True},
        {"name": "description", "type": "string", "description": "Task description", "required": False}
    ]
)
async def mcp_create_task(title: str, description: str = "") -> dict:
    """MCP Tool: Create a new task"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BACKEND_URL}/tasks",
            json={"title": title, "description": description, "completed": False},
            timeout=10.0
        )
        return response.json()


@mcp_server.tool(
    name="update_task",
    description="Update an existing task",
    parameters=[
        {"name": "task_id", "type": "string", "description": "Task ID", "required": True},
        {"name": "title", "type": "string", "description": "New title", "required": False},
        {"name": "description", "type": "string", "description": "New description", "required": False}
    ]
)
async def mcp_update_task(
    task_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None
) -> dict:
    """MCP Tool: Update a task"""
    update_data = {}
    if title:
        update_data["title"] = title
    if description:
        update_data["description"] = description

    async with httpx.AsyncClient() as client:
        response = await client.put(
            f"{BACKEND_URL}/tasks/{task_id}",
            json=update_data,
            timeout=10.0
        )
        return response.json()


@mcp_server.tool(
    name="delete_task",
    description="Delete a task",
    parameters=[
        {"name": "task_id", "type": "string", "description": "Task ID", "required": True}
    ]
)
async def mcp_delete_task(task_id: str) -> dict:
    """MCP Tool: Delete a task"""
    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"{BACKEND_URL}/tasks/{task_id}",
            timeout=10.0
        )
        return {"success": response.status_code == 200}


@mcp_server.tool(
    name="toggle_task",
    description="Toggle task completion status",
    parameters=[
        {"name": "task_id", "type": "string", "description": "Task ID", "required": True}
    ]
)
async def mcp_toggle_task(task_id: str) -> dict:
    """MCP Tool: Toggle task completion"""
    async with httpx.AsyncClient() as client:
        response = await client.patch(
            f"{BACKEND_URL}/tasks/{task_id}/toggle",
            timeout=10.0
        )
        return response.json()


# Health check
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "version": "2.0.0",
        "features": {
            "mcp_sdk": True,
            "skills": True,
            "subagents": True,
            "chat_persistence": True
        }
    }


# MCP Protocol Endpoints
@app.get("/mcp/capabilities")
def get_mcp_capabilities():
    """Get MCP server capabilities"""
    return mcp_server.get_capabilities()


@app.get("/mcp/tools/list")
def list_mcp_tools():
    """List all available MCP tools"""
    return {"tools": mcp_server.list_tools()}


@app.post("/mcp/tools/call")
async def call_mcp_tool(request: MCPToolCallRequest):
    """Call an MCP tool"""
    result = await mcp_server.call_tool(request.tool, request.arguments)
    return {
        "success": result.success,
        "result": result.result,
        "error": result.error
    }


# Skills Endpoints
@app.get("/skills/list")
def list_skills():
    """List all available skills"""
    return {"skills": skill_registry.list_skills()}


@app.post("/skills/execute/{skill_name}")
async def execute_skill(skill_name: str, query: str):
    """Execute a specific skill"""
    skill = skill_registry.get_skill(skill_name)
    if not skill:
        raise HTTPException(status_code=404, detail=f"Skill '{skill_name}' not found")

    result = await skill.execute(SkillInput(query=query))
    return {
        "success": result.success,
        "message": result.message,
        "data": result.data,
        "suggestions": result.suggestions
    }


# Sub-Agents Endpoints
@app.get("/agents/list")
def list_agents():
    """List all available sub-agents"""
    return {"agents": orchestrator.list_agents()}


# Chat Endpoint with Sub-Agent Routing
@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Main chat endpoint with sub-agent routing
    Supports conversation persistence via conversation_id
    """
    # Create sub-agent request
    agent_request = SubAgentRequest(
        query=request.query,
        context=request.context or {},
        user_id=request.user_id,
        conversation_id=request.conversation_id
    )

    # Route to appropriate sub-agent
    result = await orchestrator.route(agent_request)

    return ChatResponse(
        response=result.message,
        conversation_id=request.conversation_id,
        suggestions=result.suggestions,
        agent_used=result.agent_name
    )


# Conversation Endpoints (for chat persistence)
@app.post("/conversations")
async def create_conversation(user_id: Optional[str] = None, title: str = "New Conversation"):
    """Create a new conversation"""
    # This would connect to the backend's conversation API
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{BACKEND_URL}/conversations",
                json={"user_id": user_id, "title": title},
                timeout=10.0
            )
            if response.status_code == 200:
                return response.json()
            else:
                # If backend doesn't support conversations yet, return mock
                import uuid
                return {
                    "id": str(uuid.uuid4()),
                    "user_id": user_id,
                    "title": title
                }
        except Exception:
            import uuid
            return {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "title": title
            }


@app.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    """Get a conversation with messages"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{BACKEND_URL}/conversations/{conversation_id}",
                timeout=10.0
            )
            if response.status_code == 200:
                return response.json()
            else:
                return {"conversation_id": conversation_id, "messages": []}
        except Exception:
            return {"conversation_id": conversation_id, "messages": []}


@app.get("/conversations")
async def list_conversations(user_id: Optional[str] = None):
    """List conversations for a user"""
    async with httpx.AsyncClient() as client:
        try:
            params = {"user_id": user_id} if user_id else {}
            response = await client.get(
                f"{BACKEND_URL}/conversations",
                params=params,
                timeout=10.0
            )
            if response.status_code == 200:
                return response.json()
            else:
                return {"conversations": []}
        except Exception:
            return {"conversations": []}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
