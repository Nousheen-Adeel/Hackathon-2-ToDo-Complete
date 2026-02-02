"""
MCP SDK - Model Context Protocol Implementation
Official MCP SDK-style implementation for tool registration and execution
"""

from typing import Any, Callable, Dict, List, Optional
from pydantic import BaseModel
from dataclasses import dataclass, field
import json
import inspect


# MCP Protocol Types
class MCPToolParameter(BaseModel):
    name: str
    type: str
    description: str
    required: bool = True


class MCPTool(BaseModel):
    name: str
    description: str
    parameters: List[MCPToolParameter] = []
    handler: Optional[str] = None  # Reference to handler function name


class MCPToolResult(BaseModel):
    success: bool
    result: Any = None
    error: Optional[str] = None


class MCPMessage(BaseModel):
    role: str  # "user", "assistant", "system", "tool"
    content: str
    tool_calls: Optional[List[dict]] = None
    tool_result: Optional[MCPToolResult] = None


class MCPContext(BaseModel):
    conversation_id: Optional[str] = None
    user_id: Optional[str] = None
    messages: List[MCPMessage] = []
    metadata: Dict[str, Any] = {}


# MCP Server Class
@dataclass
class MCPServer:
    """MCP Server for registering and executing tools"""
    name: str
    version: str = "1.0.0"
    description: str = ""
    tools: Dict[str, dict] = field(default_factory=dict)
    handlers: Dict[str, Callable] = field(default_factory=dict)

    def register_tool(
        self,
        name: str,
        description: str,
        parameters: List[dict] = None,
        handler: Callable = None
    ):
        """Register a tool with the MCP server"""
        self.tools[name] = {
            "name": name,
            "description": description,
            "parameters": parameters or [],
            "inputSchema": self._generate_json_schema(parameters or [])
        }
        if handler:
            self.handlers[name] = handler

    def _generate_json_schema(self, parameters: List[dict]) -> dict:
        """Generate JSON Schema from parameter definitions"""
        properties = {}
        required = []

        for param in parameters:
            properties[param["name"]] = {
                "type": param.get("type", "string"),
                "description": param.get("description", "")
            }
            if param.get("required", True):
                required.append(param["name"])

        return {
            "type": "object",
            "properties": properties,
            "required": required
        }

    def tool(self, name: str, description: str, parameters: List[dict] = None):
        """Decorator for registering tools"""
        def decorator(func: Callable):
            self.register_tool(name, description, parameters, func)
            return func
        return decorator

    def list_tools(self) -> List[dict]:
        """List all registered tools"""
        return list(self.tools.values())

    async def call_tool(self, name: str, arguments: dict) -> MCPToolResult:
        """Execute a registered tool"""
        if name not in self.handlers:
            return MCPToolResult(
                success=False,
                error=f"Tool '{name}' not found"
            )

        try:
            handler = self.handlers[name]

            # Check if handler is async
            if inspect.iscoroutinefunction(handler):
                result = await handler(**arguments)
            else:
                result = handler(**arguments)

            return MCPToolResult(success=True, result=result)
        except Exception as e:
            return MCPToolResult(success=False, error=str(e))

    def get_capabilities(self) -> dict:
        """Get server capabilities (MCP protocol)"""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "capabilities": {
                "tools": True,
                "resources": False,
                "prompts": False
            },
            "tools": self.list_tools()
        }


# MCP Client for connecting to other MCP servers
@dataclass
class MCPClient:
    """MCP Client for connecting to MCP servers"""
    server_url: str
    timeout: float = 10.0

    async def list_tools(self) -> List[dict]:
        """List tools from remote MCP server"""
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.server_url}/mcp/tools/list",
                timeout=self.timeout
            )
            return response.json().get("tools", [])

    async def call_tool(self, name: str, arguments: dict) -> MCPToolResult:
        """Call a tool on remote MCP server"""
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.server_url}/mcp/tools/call",
                json={"tool": name, "arguments": arguments},
                timeout=self.timeout
            )
            data = response.json()
            return MCPToolResult(**data)


# Global MCP Server instance
mcp_server = MCPServer(
    name="todo-agent-mcp",
    version="1.0.0",
    description="MCP server for Todo task management"
)
