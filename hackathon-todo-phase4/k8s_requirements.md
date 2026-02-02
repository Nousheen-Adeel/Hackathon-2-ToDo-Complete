# Kubernetes Requirements for Todo Evolution - Phase 4

## Overview
This document outlines the Kubernetes resources required to deploy the Todo Evolution application to Minikube. The application consists of three main components that need to be orchestrated in a Kubernetes environment.

## Required Kubernetes Resources

### 1. Deployments

#### todo-backend-deployment
- **Replicas**: 2 (for high availability)
- **Container**: todo-backend (FastAPI)
- **Ports**: 8000
- **Resource Limits**: 
  - CPU: 500m
  - Memory: 512Mi
- **Resource Requests**:
  - CPU: 200m
  - Memory: 256Mi
- **Liveness Probe**: HTTP GET /health on port 8000
- **Readiness Probe**: HTTP GET /ready on port 8000
- **Environment Variables**: DATABASE_URL, ENVIRONMENT, LOG_LEVEL

#### todo-frontend-deployment
- **Replicas**: 2 (for high availability)
- **Container**: todo-frontend (Next.js)
- **Ports**: 3000
- **Resource Limits**:
  - CPU: 300m
  - Memory: 256Mi
- **Resource Requests**:
  - CPU: 100m
  - Memory: 128Mi
- **Liveness Probe**: HTTP GET / on port 3000
- **Readiness Probe**: HTTP GET / on port 3000
- **Environment Variables**: NEXT_PUBLIC_API_URL, NEXT_PUBLIC_APP_NAME

#### ai-agent-deployment
- **Replicas**: 1 (initially, may scale based on workload)
- **Container**: ai-agent (with MCP support)
- **Ports**: 8001 (or appropriate port for MCP)
- **Resource Limits**:
  - CPU: 1000m
  - Memory: 2Gi
- **Resource Requests**:
  - CPU: 500m
  - Memory: 1Gi
- **Liveness Probe**: HTTP GET /health on port 8001
- **Readiness Probe**: HTTP GET /ready on port 8001
- **Environment Variables**: MCP_SERVER_URL, AI_MODEL_PATH, API_KEYS, MCP_CONFIG_PATH

### 2. Services

#### todo-backend-service
- **Type**: ClusterIP
- **Port**: 8000
- **Target Port**: 8000
- **Selector**: app=todo-backend
- **Purpose**: Internal communication between frontend and backend

#### todo-frontend-service
- **Type**: LoadBalancer (for Minikube) or NodePort
- **Port**: 3000
- **Target Port**: 3000
- **Selector**: app=todo-frontend
- **Purpose**: External access to the frontend application

#### ai-agent-service
- **Type**: ClusterIP
- **Port**: 8001
- **Target Port**: 8001
- **Selector**: app=ai-agent
- **Purpose**: Internal access to the AI agent from other services

### 3. ConfigMaps

#### todo-app-config
- **Purpose**: Store non-sensitive configuration for all services
- **Data**:
  - environment: "production"
  - log_level: "INFO"
  - api_timeout: "30s"
  - frontend_public_name: "Todo Evolution App"

### 4. Secrets

#### todo-app-secrets
- **Purpose**: Store sensitive information like database credentials and API keys
- **Data** (base64 encoded):
  - database-url: "[Base64 encoded DATABASE_URL for Neon/PostgreSQL]"
  - ai-api-key: "[Base64 encoded AI service API key]"
  - mcp-server-token: "[Base64 encoded MCP server token]"
  - jwt-secret: "[Base64 encoded JWT secret]"

### 5. Ingress

#### todo-app-ingress
- **Host**: todo-evolution.local (for local development) or appropriate domain
- **Rules**:
  - Path "/api/*": Route to todo-backend-service
  - Path "/*": Route to todo-frontend-service
- **TLS**: Optional for local development, required for production
- **Annotations**: 
  - nginx.ingress.kubernetes.io/rewrite-target: /

### 6. PersistentVolume and PersistentVolumeClaim (if needed)

#### todo-pvc (if persistent storage is required)
- **Storage**: 1Gi
- **Access Modes**: ReadWriteOnce
- **Storage Class**: Standard
- **Purpose**: For storing any persistent data if required by the application

## Additional Kubernetes Resources

### 7. Namespace
- **Name**: todo-evolution
- **Purpose**: Isolate the application resources from other applications in the cluster

### 8. Network Policies (Optional but Recommended)
- **Purpose**: Restrict traffic between services
- **Rules**:
  - Allow traffic from todo-frontend to todo-backend
  - Allow traffic from todo-frontend to ai-agent (if needed)
  - Allow external traffic only to frontend service

### 9. Resource Quotas (Optional)
- **Purpose**: Limit resource consumption in the namespace
- **Limits**:
  - CPU: 2
  - Memory: 4Gi
  - Pods: 10

## Deployment Order
1. Create Namespace
2. Create Secrets
3. Create ConfigMaps
4. Create PersistentVolumeClaim (if needed)
5. Create Deployments
6. Create Services
7. Create Ingress

## Health Checks and Monitoring
- Implement proper liveness and readiness probes for all deployments
- Consider implementing Prometheus monitoring if available
- Set up basic logging aggregation
- Consider using Kubernetes dashboard for monitoring

## Scaling Considerations
- Backend service should be horizontally scalable
- Frontend service should be horizontally scalable
- AI agent may require special scaling considerations due to resource requirements
- Use Horizontal Pod Autoscaler (HPA) based on CPU/memory metrics