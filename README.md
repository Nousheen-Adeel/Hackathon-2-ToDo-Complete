# 🚀 Todo Evolution

> From CLI to Cloud - A Full Stack Todo Application built in 5 Phases

---

## 🌐 Live Demo

| Service | Link |
|---------|------|
| 🖥️ Frontend | [frontend-alpha-wheat-29.vercel.app](https://frontend-alpha-wheat-29.vercel.app/) |
| ⚡ Backend API | [huggingface.co/spaces/HayaFatima/hackathon2](https://huggingface.co/spaces/HayaFatima/hackathon2) |

---

## 📌 Project Phases

### 1️⃣ Phase 1: Console CLI App
Python command-line todo manager with in-memory storage.

**What's included:**
- Add, list, update, delete tasks
- Toggle task completion status
- Clean terminal interface

**Files:** `src/cli.py`, `src/models.py`, `src/services.py`

---

### 2️⃣ Phase 2: REST API
Converted CLI to REST API using FastAPI.

**Endpoints:**
| Method | Endpoint | Action |
|--------|----------|--------|
| GET | `/tasks` | List all tasks |
| POST | `/tasks` | Create task |
| PUT | `/tasks/{id}` | Update task |
| DELETE | `/tasks/{id}` | Delete task |
| PATCH | `/tasks/{id}/toggle` | Toggle status |

**Files:** `src/api.py`

---

### 3️⃣ Phase 3: Database Integration
Added PostgreSQL database with SQLAlchemy ORM.

**What's included:**
- Persistent data storage
- SQLAlchemy models
- Database migrations
- Connection pooling

**Files:** `src/database.py`, `src/models.py`

---

### 4️⃣ Phase 4: Frontend + Containerization
Built modern UI with Next.js and containerized with Docker/Kubernetes.

**What's included:**
- Responsive Next.js + Tailwind CSS UI
- Task dashboard with filters
- Docker Compose setup
- Kubernetes manifests for Minikube deployment

**Files:** `hackathon-todo-phase4/frontend/`, `hackathon-todo-phase4/docker-compose.yml`, `k8s-manifests/`

---

### 5️⃣ Phase 5: Authentication & AI Agent
Added JWT authentication and AI-powered chat assistant.

**What's included:**
- User registration & login (JWT tokens)
- Protected API routes
- AI chat agent using MCP SDK
- Natural language task management

**Endpoints:**
| Method | Endpoint | Action |
|--------|----------|--------|
| POST | `/auth/register` | Register user |
| POST | `/auth/login` | Login & get token |
| GET | `/auth/me` | Get current user |
| POST | `/chat` | AI chat |

**Files:** `hackathon-todo-phase4/backend/auth.py`, `hackathon-todo-phase4/ai-agent/`

---

## ✨ Features

- ➕ Create, edit, delete tasks
- ✅ Mark tasks complete/incomplete
- 🔐 User authentication (JWT)
- 🤖 AI-powered task management via chat
- 📱 Responsive design
- 🐳 Docker & Kubernetes ready

---

## 🛠️ Tech Stack

| Category | Technologies |
|----------|--------------|
| **Backend** | Python, FastAPI, PostgreSQL, SQLAlchemy, JWT |
| **Frontend** | Next.js 14, TypeScript, Tailwind CSS |
| **AI** | OpenAI GPT-4, MCP SDK |
| **DevOps** | Docker, Kubernetes, Vercel, Hugging Face |

---

## 📁 Project Structure

```
├── src/                      # Phase 1-3 (CLI, API, Database)
├── hackathon-todo-phase4/    # Phase 4-5
│   ├── frontend/             # Next.js app
│   ├── backend/              # FastAPI + Auth
│   └── ai-agent/             # MCP SDK agent
├── k8s-manifests/            # Kubernetes configs
└── specs/                    # Phase specifications
```

---

## 🏃 Quick Run

```bash
# Clone
git clone https://github.com/Nousheen-Adeel/Hackathon-2-ToDo-Complete.git
cd Hackathon-2-ToDo-Complete

# Run with Docker
cd hackathon-todo-phase4
docker-compose up -d

# Access
# Frontend: http://localhost:3000
# Backend:  http://localhost:8000
```

---

## 👩‍💻 Author

**Nousheen Adeel**
[![GitHub](https://img.shields.io/badge/GitHub-Nousheen--Adeel-black?style=flat&logo=github)](https://github.com/Nousheen-Adeel)

---

<p align="center">Made with ❤️ for Hackathon</p>
