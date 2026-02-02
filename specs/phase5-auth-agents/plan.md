# Phase 5 Implementation Plan

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (React)                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │   Auth UI   │  │   Task UI   │  │      Chat Widget        │  │
│  └──────┬──────┘  └──────┬──────┘  └───────────┬─────────────┘  │
└─────────┼────────────────┼─────────────────────┼────────────────┘
          │                │                     │
          ▼                ▼                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                       Backend API (FastAPI)                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │ Auth Module │  │ Task CRUD   │  │  Chat Persistence       │  │
│  │   (JWT)     │  │ Endpoints   │  │  Conversations API      │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
          │                │                     │
          ▼                ▼                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PostgreSQL Database                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │    users    │  │    tasks    │  │  conversations/messages │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      AI Agent Service                            │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                    Agent Orchestrator                        ││
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────┐ ││
│  │  │ Task Manager │ │ Conversation │ │     Analytics        │ ││
│  │  │   Agent      │ │    Agent     │ │       Agent          │ ││
│  │  └──────┬───────┘ └──────┬───────┘ └──────────┬───────────┘ ││
│  └─────────┼────────────────┼────────────────────┼─────────────┘│
│            │                │                    │              │
│  ┌─────────┼────────────────┼────────────────────┼─────────────┐│
│  │                    Skill Registry                            ││
│  │  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────────┐ ││
│  │  │ Create │ │  List  │ │ Delete │ │ Update │ │   Toggle   │ ││
│  │  └────────┘ └────────┘ └────────┘ └────────┘ └────────────┘ ││
│  └─────────────────────────────────────────────────────────────┘│
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                      MCP SDK Server                          ││
│  │  Tools: get_tasks, create_task, update_task, delete_task    ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

## Implementation Approach

### 1. Authentication Module (auth.py)
- Implement secure password hashing (SHA-256 + salt)
- Create JWT token generation (access + refresh)
- Add token validation middleware
- Provide FastAPI dependencies for protected routes

### 2. Chat Persistence Module (chat_persistence.py)
- Create conversations table schema
- Create messages table schema
- Implement CRUD operations for conversations
- Implement message storage and retrieval

### 3. MCP SDK Module (mcp_sdk.py)
- Define MCP protocol types (Tool, Result, Context)
- Implement MCPServer class with tool registration
- Create JSON Schema generation for tools
- Add async tool execution support

### 4. Skills Module (skills.py)
- Define Skill base class with execute() method
- Implement concrete skills for each operation
- Create SkillRegistry for skill management
- Add keyword-based skill matching

### 5. Sub-Agents Module (subagents.py)
- Define SubAgent base class
- Implement TaskManagementAgent
- Implement ConversationAgent
- Implement AnalyticsAgent
- Create AgentOrchestrator for routing

## Integration Points

### Backend ↔ AI Agent
- AI Agent calls Backend API for task operations
- Backend stores conversation history
- Shared database for persistence

### Frontend ↔ Backend
- JWT tokens in Authorization header
- Conversation ID tracking for chat sessions
- Real-time task updates

## Security Measures
1. Password hashing with unique salts
2. JWT signing with secret key
3. Token expiration handling
4. CORS configuration
5. Parameterized SQL queries
