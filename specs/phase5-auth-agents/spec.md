# Phase 5: Authentication, MCP SDK, Skills & Sub-Agents

## Overview
This phase adds enterprise-grade features to the Todo application including JWT-based authentication, Model Context Protocol (MCP) SDK integration, modular skill-based architecture, and sub-agent orchestration.

## Features

### 1. Better Auth with JWT Authentication
- **User Registration**: Email/password registration with secure hashing
- **User Login**: JWT-based stateless authentication
- **Token Refresh**: Automatic token renewal with refresh tokens
- **Protected Routes**: Optional authentication for endpoints

#### Authentication Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/auth/register` | POST | Register new user |
| `/auth/login` | POST | Login and get tokens |
| `/auth/refresh` | POST | Refresh access token |
| `/auth/me` | GET | Get current user info |

#### Token Structure
- **Access Token**: 30-minute expiry, used for API requests
- **Refresh Token**: 7-day expiry, used to get new access tokens

### 2. MCP SDK (Model Context Protocol)
Official MCP SDK-style implementation for tool registration and execution.

#### MCP Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/mcp/capabilities` | GET | Get server capabilities |
| `/mcp/tools/list` | GET | List all MCP tools |
| `/mcp/tools/call` | POST | Execute an MCP tool |

#### Registered MCP Tools
- `get_tasks` - Retrieve all tasks
- `create_task` - Create a new task
- `update_task` - Update existing task
- `delete_task` - Delete a task
- `toggle_task` - Toggle completion status

### 3. Skills Architecture
Modular skill-based system for handling specific capabilities.

#### Available Skills
| Skill | Description | Keywords |
|-------|-------------|----------|
| `task_creation` | Creates new tasks | add task, create task |
| `task_listing` | Lists all tasks | list tasks, show tasks |
| `task_deletion` | Deletes tasks | delete task, remove task |
| `task_update` | Updates tasks | update task, edit task |
| `task_toggle` | Toggles completion | complete task, done |
| `help` | Provides help | help, commands |
| `greeting` | Handles greetings | hello, hi |

#### Skills Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/skills/list` | GET | List all skills |
| `/skills/execute/{name}` | POST | Execute specific skill |

### 4. Sub-Agents Architecture
Specialized agents for different domains.

#### Available Sub-Agents
| Agent | Description | Domains |
|-------|-------------|---------|
| `task_manager` | Task operations | task, todo, add, delete |
| `conversation` | General chat | hello, help, thanks |
| `analytics` | Task analytics | stats, summary, report |

#### Agent Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/agents/list` | GET | List all agents |

### 5. Chat Persistence
Database-persisted conversations for stateless chat endpoints.

#### Conversation Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/conversations` | POST | Create conversation |
| `/conversations` | GET | List user conversations |
| `/conversations/{id}` | GET | Get conversation |
| `/conversations/{id}` | DELETE | Delete conversation |
| `/conversations/{id}/messages` | POST | Add message |
| `/conversations/{id}/messages` | GET | Get messages |

#### Database Schema
```sql
-- Users table
CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Conversations table
CREATE TABLE conversations (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36),
    title VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Messages table
CREATE TABLE messages (
    id VARCHAR(36) PRIMARY KEY,
    conversation_id VARCHAR(36) REFERENCES conversations(id),
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Technical Requirements

### Dependencies
- **Backend**: FastAPI, PyJWT, psycopg2-binary, httpx
- **AI Agent**: FastAPI, httpx, pydantic

### Environment Variables
```env
JWT_SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:pass@host:5432/db
```

## Security Considerations
- Passwords hashed with SHA-256 + salt
- JWT tokens signed with HS256 algorithm
- CORS enabled for cross-origin requests
- SQL injection prevention via parameterized queries
