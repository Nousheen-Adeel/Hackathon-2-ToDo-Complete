#!/bin/bash

# Todo Evolution Kubernetes Deployment Script

echo "🚀 Starting deployment of Todo Evolution to Kubernetes..."

# Create namespace
echo "📦 Creating namespace..."
kubectl apply -f namespace.yaml

# Wait for namespace to be created
sleep 5

# Apply PV and PVC
echo "💾 Creating PersistentVolume and PersistentVolumeClaim..."
kubectl apply -f pv-pvc.yaml

# Apply secrets
echo "🔒 Creating secrets..."
kubectl apply -f secrets.yaml

# Apply ConfigMap
echo "⚙️ Creating ConfigMap..."
kubectl apply -f configmap.yaml

# Apply PostgreSQL
echo "🐘 Deploying PostgreSQL..."
kubectl apply -f postgres.yaml

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
kubectl wait --for=condition=ready pod -l app=postgres -n todo-evolution --timeout=120s

# Apply backend
echo "🔧 Deploying Backend..."
kubectl apply -f backend.yaml

# Wait for backend to be ready
echo "⏳ Waiting for Backend to be ready..."
kubectl wait --for=condition=ready pod -l app=todo-backend -n todo-evolution --timeout=120s

# Apply AI agent
echo "🤖 Deploying AI Agent..."
kubectl apply -f ai-agent.yaml

# Wait for AI agent to be ready
echo "⏳ Waiting for AI Agent to be ready..."
kubectl wait --for=condition=ready pod -l app=ai-agent -n todo-evolution --timeout=120s

# Apply frontend
echo "🎨 Deploying Frontend..."
kubectl apply -f frontend.yaml

# Wait for frontend to be ready
echo "⏳ Waiting for Frontend to be ready..."
kubectl wait --for=condition=ready pod -l app=todo-frontend -n todo-evolution --timeout=120s

echo "✅ Deployment completed!"

# Show status
echo "📋 Checking deployment status..."
kubectl get pods -n todo-evolution
kubectl get services -n todo-evolution

echo "🌐 To access the application, run: minikube service todo-frontend -n todo-evolution"