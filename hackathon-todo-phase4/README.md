# Todo Evolution - Phase 4: Cloud-Native Deployment

## Overview
This phase focuses on deploying the Todo Evolution application to Kubernetes using Minikube. The application consists of three main components: FastAPI backend, Next.js frontend, and AI agent with MCP support.

## Architecture
- **Backend**: FastAPI application with PostgreSQL database
- **Frontend**: Next.js application with task management UI
- **AI Agent**: MCP-enabled agent for task management via natural language
- **Database**: PostgreSQL for persistent task storage

## Features Implemented
- ✅ Full CRUD operations for tasks
- ✅ Natural language task management via AI chat
- ✅ Real-time task synchronization
- ✅ Containerized deployment with Docker
- ✅ Kubernetes orchestration with Minikube
- ✅ Health checks and monitoring
- ✅ Environment configuration management

## Prerequisites
- Docker installed and running
- Minikube installed
- kubectl installed
- kubectl configured to use Minikube context

## Deployment Steps

### 1. Start Minikube
```bash
minikube start
```

### 2. Build Docker Images
```bash
# Build backend image
docker build -f backend/Dockerfile -t todo-backend:latest backend/.

# Build frontend image
docker build -f frontend/Dockerfile -t todo-frontend:latest frontend/.

# Build AI agent image
docker build -f ai-agent/Dockerfile -t ai-agent:latest ai-agent/.
```

### 3. Load Images into Minikube
```bash
# Load images into Minikube's Docker environment
minikube image load todo-backend:latest
minikube image load todo-frontend:latest
minikube image load ai-agent:latest
```

### 4. Update Secrets with Real Values
Before applying the secrets, you need to encode your actual database URL:

```bash
# Encode your database URL (replace with your actual URL)
echo -n 'your_actual_database_url' | base64
```

Then update the `k8s/secrets.yaml` file with the encoded values before applying.

### 5. Apply Kubernetes Manifests
```bash
# Apply secrets and configmaps first
kubectl apply -f k8s/secrets.yaml

# Apply backend deployment and service
kubectl apply -f k8s/backend.yaml

# Apply AI agent deployment
kubectl apply -f k8s/agent.yaml

# Apply frontend deployment and service
kubectl apply -f k8s/frontend.yaml
```

### 6. Verify Deployment
```bash
# Check all pods
kubectl get pods

# Check all services
kubectl get services

# Check logs for any specific pod
kubectl logs -l app=todo-backend
```

### 7. Access the Application
```bash
# Get the frontend service URL
minikube service todo-frontend --url
```

## Local Testing with Docker Compose
Before deploying to Kubernetes, you can test the container connectivity locally:

```bash
docker-compose up --build
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- AI Agent: http://localhost:8001

## Task Management Commands
The AI assistant understands these commands:
- **Add Task**: "add task [task description]"
- **Update Task**: "update task [current description] to [new description]"
- **Delete Task**: "delete task [task description]"
- **List Tasks**: "list tasks" or "show tasks"

## Troubleshooting

### Common Issues
1. **ImagePullBackOff**: Make sure images are loaded into Minikube with `minikube image load`
2. **Service not accessible**: Check if the service is running with `kubectl get services`
3. **Database connection issues**: Verify the DATABASE_URL in secrets is correctly encoded

### Useful Commands
```bash
# Get detailed information about a pod
kubectl describe pod <pod-name>

# Get logs from a specific container
kubectl logs <pod-name> -c <container-name>

# Execute commands inside a running pod
kubectl exec -it <pod-name> -- /bin/sh

# Port forward to access services locally
kubectl port-forward svc/todo-backend 8000:8000
```

## Cleanup
To remove all resources:
```bash
kubectl delete -f k8s/
```