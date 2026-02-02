#!/bin/bash

# Phase 4 Deployment Script

echo "🚀 Starting deployment of Todo Evolution - Phase 4..."

# Check prerequisites
echo "🔍 Checking prerequisites..."

if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl is not installed. Please install kubectl first."
    exit 1
fi

if ! command -v minikube &> /dev/null; then
    echo "❌ minikube is not installed. Please install minikube first."
    exit 1
fi

echo "✅ All prerequisites are installed."

# Start minikube
echo "☸️ Starting Minikube..."
minikube start

# Build Docker images
echo "🐳 Building Docker images..."

# Build backend
cd ./backend
docker build -t todo-backend:latest .
cd ..

# Build frontend
cd ./frontend
docker build -t todo-frontend:latest .
cd ..

# Build AI agent
cd ./ai-agent
docker build -t ai-agent:latest .
cd ..

# Load images into minikube
echo "📥 Loading images into Minikube..."
minikube image load todo-backend:latest
minikube image load todo-frontend:latest
minikube image load ai-agent:latest

# Apply Kubernetes configurations
echo "⚙️ Applying Kubernetes configurations..."

# Apply secrets first
kubectl apply -f k8s/secrets.yaml

# Apply backend
kubectl apply -f k8s/backend.yaml

# Apply AI agent
kubectl apply -f k8s/agent.yaml

# Apply frontend
kubectl apply -f k8s/frontend.yaml

echo "✅ Deployment completed!"

# Show status
echo "📋 Checking deployment status..."
kubectl get pods
kubectl get services

echo "🌐 To access the application, run: minikube service todo-frontend --url"