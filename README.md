# 🚀 Todo Evolution - Complete Full Stack Application

> A progressive Todo application built through 5 phases - from simple CLI to AI-powered microservices!

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Phase 1: Console CLI App](#-phase-1-console-cli-app)
- [Phase 2: REST API](#-phase-2-rest-api)
- [Phase 3: Database Integration](#-phase-3-database-integration)
- [Phase 4: Frontend UI + Kubernetes](#-phase-4-frontend-ui--kubernetes)
- [Phase 5: Auth & AI + Cloud Deployment](#-phase-5-auth--ai--cloud-deployment)
- [Tech Stack](#-tech-stack)
- [Author](#-author)

---

## 🌟 Overview

| Phase | Name | Description | Deployment |
|:-----:|------|-------------|------------|
| 1️⃣ | Console CLI | Python command-line todo app | Local |
| 2️⃣ | REST API | FastAPI web endpoints | Local |
| 3️⃣ | Database | PostgreSQL persistent storage | Docker |
| 4️⃣ | Frontend | Next.js beautiful UI | **Minikube/Kubernetes** |
| 5️⃣ | Auth & AI | JWT login + AI chat agent | **Vercel + Hugging Face** |

---

## 📁 Project Structure

```
📦 hackathon-2/
├── 📂 src/                        # Phase 1-3 Core Backend
├── 📂 hackathon-phase-2-and-3/    # Phase 2-3 with Frontend
├── 📂 hackathon-todo-phase4/      # Phase 4-5 Complete App
├── 📂 k8s-manifests/              # Kubernetes Configs
├── 📂 specs/                      # Phase Specifications
└── 📂 tests/                      # Unit Tests
```

---

# 1️⃣ Phase 1: Console CLI App

## 📝 Description

Simple command-line Todo application with **in-memory storage**. Users can manage tasks directly from terminal.

## ✨ Features

| Feature | Description |
|---------|-------------|
| ➕ Add Task | Create new task with title & description |
| 📋 List Tasks | View all tasks with status |
| ✏️ Update Task | Edit task title or description |
| 🗑️ Delete Task | Remove task by ID |
| ✅ Toggle Status | Mark task complete/incomplete |

## 📂 Files

```
📂 src/
├── 📄 models.py      # Task data model
├── 📄 services.py    # Business logic (CRUD)
├── 📄 cli.py         # Command line interface
└── 📄 utils.py       # Helper functions
```

## ▶️ How to Run Phase 1

```powershell
# Step 1: Go to project folder
cd hackathon-2

# Step 2: Create virtual environment
python -m venv venv

# Step 3: Activate virtual environment
# Windows:
.\venv\Scripts\Activate.ps1
# Linux/Mac:
source venv/bin/activate

# Step 4: Install dependencies
pip install -r requirements.txt

# Step 5: Run CLI app
python -m src.cli
```

## 💻 CLI Commands

```bash
add "Buy groceries" "Milk, eggs, bread"    # Add task
list                                        # List all tasks
update 1 "Buy groceries" "Updated desc"    # Update task
toggle 1                                    # Toggle status
delete 1                                    # Delete task
```

---

# 2️⃣ Phase 2: REST API

## 📝 Description

Convert CLI app to **REST API** using FastAPI. Now tasks can be managed via HTTP requests!

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🌐 HTTP Endpoints | RESTful API design |
| 📊 JSON Responses | Standard JSON format |
| ✅ Validation | Pydantic data validation |
| 📖 Auto Docs | Swagger UI documentation |

## 📂 Files

```
📂 src/
├── 📄 api.py         # FastAPI routes
├── 📄 models.py      # Pydantic schemas
└── 📄 services.py    # Business logic
```

## ▶️ How to Run Phase 2

```powershell
# Step 1: Activate virtual environment
.\venv\Scripts\Activate.ps1    # Windows
source venv/bin/activate       # Linux/Mac

# Step 2: Run FastAPI server
uvicorn src.api:app --reload --port 8000

# Step 3: Open Swagger UI
# http://localhost:8000/docs
```

## 🔗 API Endpoints

| Method | Endpoint | Description |
|:------:|----------|-------------|
| `GET` | `/tasks` | 📋 Get all tasks |
| `POST` | `/tasks` | ➕ Create new task |
| `GET` | `/tasks/{id}` | 🔍 Get task by ID |
| `PUT` | `/tasks/{id}` | ✏️ Update task |
| `DELETE` | `/tasks/{id}` | 🗑️ Delete task |
| `PATCH` | `/tasks/{id}/toggle` | ✅ Toggle status |

## 🧪 Test API with cURL

```powershell
# Get all tasks
curl http://localhost:8000/tasks

# Create task
curl -X POST http://localhost:8000/tasks -H "Content-Type: application/json" -d '{"title": "Learn FastAPI", "description": "Complete tutorial"}'

# Toggle task
curl -X PATCH http://localhost:8000/tasks/1/toggle
```

---

# 3️⃣ Phase 3: Database Integration

## 📝 Description

Replace in-memory storage with **PostgreSQL database** using SQLAlchemy ORM for persistent data storage.

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🗄️ PostgreSQL | Relational database |
| 🔗 SQLAlchemy | Python ORM |
| 💾 Persistence | Data survives restarts |
| 🐳 Docker | Containerized database |

## 📂 Files

```
📂 src/
├── 📄 database.py    # SQLAlchemy setup & connection
├── 📄 models.py      # ORM models
├── 📄 services.py    # Database operations
└── 📄 api.py         # Same API endpoints
```

## ▶️ How to Run Phase 3

```powershell
# Step 1: Start PostgreSQL with Docker
docker run -d --name todo-postgres -e POSTGRES_DB=todo_db -e POSTGRES_USER=todo_user -e POSTGRES_PASSWORD=todo_password -p 5432:5432 postgres:15

# Step 2: Set environment variable
# Windows PowerShell:
$env:DATABASE_URL="postgresql://todo_user:todo_password@localhost:5432/todo_db"

# Linux/Mac:
export DATABASE_URL="postgresql://todo_user:todo_password@localhost:5432/todo_db"

# Step 3: Run FastAPI server
uvicorn src.api:app --reload --port 8000

# Step 4: Test database
# http://localhost:8000/docs
```

## 🗄️ Database Schema

```sql
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    completed BOOLEAN DEFAULT FALSE
);
```

---

# 4️⃣ Phase 4: Frontend UI + Kubernetes

## 📝 Description

Beautiful **Next.js frontend** with Tailwind CSS + **Kubernetes deployment** with Minikube!

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🎨 Modern UI | Clean white theme |
| 📱 Responsive | Works on all devices |
| ⚡ Real-time | Instant updates |
| ☸️ Kubernetes | Container orchestration |

## 📂 Files

```
📂 hackathon-todo-phase4/
├── 📂 frontend/          # Next.js app
├── 📂 backend/           # FastAPI backend
├── 📂 k8s/               # Kubernetes manifests
└── 📄 docker-compose.yml # Docker setup

📂 k8s-manifests/         # Production K8s configs
├── 📄 namespace.yaml
├── 📄 postgres.yaml
├── 📄 backend.yaml
├── 📄 frontend.yaml
├── 📄 ai-agent.yaml
└── 📄 deploy.sh
```

---

## ▶️ Option A: Run with Docker Compose (Easy)

```powershell
# Step 1: Go to phase 4 folder
cd hackathon-todo-phase4

# Step 2: Start all services
docker-compose up -d --build

# Step 3: Access applications
# 🌐 Frontend: http://localhost:3000
# 🔌 Backend:  http://localhost:8000
# 🤖 AI Agent: http://localhost:8001

# Stop services
docker-compose down
```

---

## ☸️ Option B: Deploy with Minikube & Kubernetes

### 📋 Prerequisites

```powershell
# Install Minikube (Windows - using Chocolatey)
choco install minikube

# OR download from: https://minikube.sigs.k8s.io/docs/start/

# Install kubectl
choco install kubernetes-cli

# Verify installations
minikube version
kubectl version --client
```

### 🚀 Step-by-Step Kubernetes Deployment

```powershell
# Step 1: Start Minikube
minikube start --driver=docker --memory=4096 --cpus=2

# Step 2: Enable addons
minikube addons enable ingress
minikube addons enable metrics-server

# Step 3: Set Docker to use Minikube's Docker daemon
# PowerShell:
& minikube -p minikube docker-env --shell powershell | Invoke-Expression

# Bash:
eval $(minikube docker-env)

# Step 4: Go to k8s manifests folder
cd k8s-manifests

# Step 5: Create namespace
kubectl apply -f namespace.yaml

# Step 6: Deploy PostgreSQL
kubectl apply -f pv-pvc.yaml
kubectl apply -f postgres.yaml

# Step 7: Wait for PostgreSQL to be ready
kubectl wait --for=condition=ready pod -l app=postgres -n todo-app --timeout=120s

# Step 8: Deploy Backend
kubectl apply -f backend.yaml

# Step 9: Deploy Frontend
kubectl apply -f frontend.yaml

# Step 10: Deploy AI Agent
kubectl apply -f ai-agent.yaml

# Step 11: Check all pods are running
kubectl get pods -n todo-app

# Step 12: Get service URLs
minikube service list -n todo-app
```

### 🔗 Access Application on Minikube

```powershell
# Get Frontend URL
minikube service todo-frontend -n todo-app --url

# Get Backend URL
minikube service todo-backend -n todo-app --url

# Get AI Agent URL
minikube service todo-ai-agent -n todo-app --url

# OR open directly in browser
minikube service todo-frontend -n todo-app
```

### 📊 Kubernetes Commands Cheatsheet

```powershell
# View all resources
kubectl get all -n todo-app

# View pods
kubectl get pods -n todo-app

# View logs
kubectl logs -f deployment/todo-backend -n todo-app
kubectl logs -f deployment/todo-frontend -n todo-app

# Describe pod (for debugging)
kubectl describe pod <pod-name> -n todo-app

# Scale deployment
kubectl scale deployment todo-backend --replicas=3 -n todo-app

# Delete all resources
kubectl delete namespace todo-app

# Stop Minikube
minikube stop

# Delete Minikube cluster
minikube delete
```

### 🔧 Minikube Dashboard

```powershell
# Open Kubernetes Dashboard
minikube dashboard
```

---

# 5️⃣ Phase 5: Auth & AI + Cloud Deployment

## 📝 Description

Enterprise features: **JWT Authentication** + **AI Agent** with deployments to **Vercel** (Frontend) and **Hugging Face Spaces** (Backend/AI)!

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔐 JWT Auth | Secure token-based login |
| 🤖 AI Agent | Natural language task management |
| 🚀 Vercel | Frontend cloud deployment |
| 🤗 Hugging Face | Backend/AI deployment |

## 📂 Files

```
📂 hackathon-todo-phase4/
├── 📂 backend/
│   ├── 📄 main.py              # FastAPI with all routes
│   ├── 📄 auth.py              # JWT authentication
│   └── 📄 requirements.txt
│
├── 📂 frontend/
│   ├── 📄 package.json
│   └── 📂 src/
│
└── 📂 ai-agent/
    ├── 📄 main.py              # AI agent server
    ├── 📄 mcp_sdk.py           # MCP SDK
    └── 📄 requirements.txt
```

---

## 🔐 Authentication Endpoints

| Method | Endpoint | Description |
|:------:|----------|-------------|
| `POST` | `/auth/register` | 📝 Register new user |
| `POST` | `/auth/login` | 🔑 Login & get tokens |
| `POST` | `/auth/refresh` | 🔄 Refresh access token |
| `GET` | `/auth/me` | 👤 Get current user |

---

## 🚀 Deploy Frontend to Vercel

### 📋 Prerequisites
- Vercel account: https://vercel.com/signup
- GitHub repository connected

### Step-by-Step Vercel Deployment

```powershell
# Step 1: Install Vercel CLI
npm install -g vercel

# Step 2: Go to frontend folder
cd hackathon-todo-phase4/frontend

# Step 3: Login to Vercel
vercel login

# Step 4: Create .env.local for production
echo "NEXT_PUBLIC_API_URL=https://your-backend-url.hf.space" > .env.local

# Step 5: Deploy to Vercel
vercel

# Step 6: Follow prompts:
# ? Set up and deploy? Yes
# ? Which scope? Select your account
# ? Link to existing project? No
# ? Project name? todo-evolution-frontend
# ? Directory? ./
# ? Override settings? No

# Step 7: Deploy to production
vercel --prod

# 🎉 Your frontend is live at: https://todo-evolution-frontend.vercel.app
```

### Vercel Environment Variables (Dashboard)

Go to: **Vercel Dashboard → Project → Settings → Environment Variables**

```
NEXT_PUBLIC_API_URL = https://your-backend.hf.space
NEXT_PUBLIC_AI_AGENT_URL = https://your-ai-agent.hf.space
```

---

## 🤗 Deploy Backend to Hugging Face Spaces

### 📋 Prerequisites
- Hugging Face account: https://huggingface.co/join
- Create new Space: https://huggingface.co/new-space

### Step 1: Create Hugging Face Space

1. Go to https://huggingface.co/new-space
2. **Space name**: `todo-backend`
3. **License**: MIT
4. **Select SDK**: Docker
5. **Hardware**: CPU Basic (Free)
6. Click **Create Space**

### Step 2: Create Dockerfile for Backend

Create `Dockerfile` in `hackathon-todo-phase4/backend/`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 7860

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
```

### Step 3: Push to Hugging Face

```powershell
# Step 1: Install Git LFS (if not installed)
git lfs install

# Step 2: Clone your HF Space
git clone https://huggingface.co/spaces/YOUR_USERNAME/todo-backend
cd todo-backend

# Step 3: Copy backend files
cp -r ../hackathon-todo-phase4/backend/* .

# Step 4: Create README.md for HF Space
@"
---
title: Todo Backend API
emoji: 🚀
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
---

# Todo Backend API
FastAPI backend for Todo Evolution app.
"@ | Out-File -FilePath README.md -Encoding utf8

# Step 5: Add and push
git add .
git commit -m "Deploy todo backend"
git push

# 🎉 Backend live at: https://YOUR_USERNAME-todo-backend.hf.space
```

### Step 4: Set Hugging Face Secrets

Go to: **Space Settings → Variables and secrets**

```
DATABASE_URL = your-neon-db-url
JWT_SECRET_KEY = your-secret-key
```

---

## 🤗 Deploy AI Agent to Hugging Face Spaces

### Step 1: Create Another Space

1. Go to https://huggingface.co/new-space
2. **Space name**: `todo-ai-agent`
3. **SDK**: Docker
4. Click **Create Space**

### Step 2: Create Dockerfile for AI Agent

Create `Dockerfile` in `hackathon-todo-phase4/ai-agent/`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 7860

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
```

### Step 3: Push AI Agent to HF

```powershell
# Clone HF Space
git clone https://huggingface.co/spaces/YOUR_USERNAME/todo-ai-agent
cd todo-ai-agent

# Copy ai-agent files
cp -r ../hackathon-todo-phase4/ai-agent/* .

# Create README
@"
---
title: Todo AI Agent
emoji: 🤖
colorFrom: purple
colorTo: pink
sdk: docker
pinned: false
---

# Todo AI Agent
MCP SDK powered AI agent for Todo app.
"@ | Out-File -FilePath README.md -Encoding utf8

# Push
git add .
git commit -m "Deploy AI agent"
git push

# 🎉 AI Agent live at: https://YOUR_USERNAME-todo-ai-agent.hf.space
```

### Step 4: Set AI Agent Secrets

Go to: **Space Settings → Variables and secrets**

```
OPENAI_API_KEY = your-openai-api-key
TODO_BACKEND_URL = https://YOUR_USERNAME-todo-backend.hf.space
```

---

## 🌐 Live Deployment Links (After Deployment)

| Service | Platform | URL |
|---------|----------|-----|
| 🌐 Frontend | Vercel | `https://todo-evolution.vercel.app` |
| 🔌 Backend | Hugging Face | `https://username-todo-backend.hf.space` |
| 🤖 AI Agent | Hugging Face | `https://username-todo-ai-agent.hf.space` |

---

## 🔗 Connect All Services

### Update Frontend Environment (Vercel)

```
NEXT_PUBLIC_API_URL = https://username-todo-backend.hf.space
NEXT_PUBLIC_AI_AGENT_URL = https://username-todo-ai-agent.hf.space
```

### Update AI Agent Environment (Hugging Face)

```
TODO_BACKEND_URL = https://username-todo-backend.hf.space
```

---

## 💬 Test AI Chat

```
You: "Add a task to buy groceries"
AI: "✅ Task created: Buy groceries"

You: "Show all my tasks"
AI: "📋 Your tasks:
     1. Buy groceries - Pending
     2. Learn Python - Completed"

You: "Mark task 1 as complete"
AI: "✅ Task 'Buy groceries' marked as complete!"
```

---

# 🛠️ Tech Stack

## Backend
| Technology | Purpose |
|------------|---------|
| 🐍 Python 3.11 | Programming language |
| ⚡ FastAPI | Web framework |
| 🗄️ PostgreSQL | Database |
| 🔗 SQLAlchemy | ORM |
| 🔐 JWT | Authentication |

## Frontend
| Technology | Purpose |
|------------|---------|
| ⚛️ Next.js 14 | React framework |
| 📘 TypeScript | Type safety |
| 🎨 Tailwind CSS | Styling |

## AI/ML
| Technology | Purpose |
|------------|---------|
| 🧠 OpenAI GPT-4 | Language model |
| 🔌 MCP SDK | Tool integration |

## DevOps
| Technology | Purpose |
|------------|---------|
| 🐳 Docker | Containerization |
| ☸️ Kubernetes | Orchestration |
| 🚀 Vercel | Frontend hosting |
| 🤗 Hugging Face | Backend hosting |

---

# ⚙️ Environment Variables

## Local Development (.env)

```env
# Database
DATABASE_URL=postgresql://todo_user:todo_password@localhost:5432/todo_db

# Authentication
JWT_SECRET_KEY=your-super-secret-key-here

# AI Agent
OPENAI_API_KEY=your-openai-api-key-here
```

## Production (Vercel)

```env
NEXT_PUBLIC_API_URL=https://username-todo-backend.hf.space
NEXT_PUBLIC_AI_AGENT_URL=https://username-todo-ai-agent.hf.space
```

## Production (Hugging Face)

```env
DATABASE_URL=your-neon-db-url
JWT_SECRET_KEY=your-secret-key
OPENAI_API_KEY=your-openai-key
```

---

# 🧪 Running Tests

```powershell
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_api.py -v

# Run with coverage
pytest tests/ --cov=src
```

---

# 🚀 Quick Start Summary

| Phase | Command |
|-------|---------|
| **Phase 1** | `python -m src.cli` |
| **Phase 2** | `uvicorn src.api:app --reload --port 8000` |
| **Phase 3** | `docker run postgres` + `uvicorn` |
| **Phase 4** | `docker-compose up -d` OR `minikube start` |
| **Phase 5** | Deploy to **Vercel** + **Hugging Face** |

---

## 👩‍💻 Author

**Nousheen Adeel**

[![GitHub](https://img.shields.io/badge/GitHub-Nousheen--Adeel-black?style=flat&logo=github)](https://github.com/Nousheen-Adeel)

---

## 📄 License

This project is for **educational** and **hackathon** purposes.

---

<p align="center">
  Made with ❤️ for Hackathon
</p>
