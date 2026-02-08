# Phase IV: Local Kubernetes Deployment - Requirements

## Objective
Deploy the Todo AI Chatbot on a local Kubernetes cluster using Minikube, Helm Charts, with AI-assisted DevOps tools (Gordon, kubectl-ai, Kagent).

## Functional Requirements

### FR-1: Containerization
- Containerize frontend and backend applications using Docker
- Use multi-stage builds for minimal image size
- Run containers as non-root user for security
- Include health check endpoints in containers
- Optionally use Docker AI Agent (Gordon) for AI-assisted Docker operations

### FR-2: Helm Charts
- Create Helm chart for backend deployment
- Create Helm chart for frontend deployment
- Configurable via values.yaml
- Support environment-specific overrides
- Environment variables via ConfigMaps and Secrets

### FR-3: Kubernetes Resources
- Deployments for frontend and backend with configurable replicas
- Services (ClusterIP for backend, NodePort for frontend)
- ConfigMaps for non-sensitive configuration
- Secrets for DATABASE_URL, BETTER_AUTH_SECRET, OPENAI_API_KEY
- Liveness and Readiness probes for health monitoring
- Optional Ingress for unified access

### FR-4: AI-Assisted DevOps
- Use kubectl-ai for intelligent Kubernetes operations
- Use Kagent for cluster analysis and optimization
- Document AI tool usage patterns and commands

### FR-5: Minikube Deployment
- All services deployable on Minikube
- Automated setup and teardown scripts
- Load images into Minikube registry
- Port forwarding for local access

## Non-Functional Requirements

### NFR-1: Image Size
- Backend image < 500MB
- Frontend image < 500MB

### NFR-2: Startup Time
- Backend container ready < 30 seconds
- Frontend container ready < 60 seconds

### NFR-3: Resource Limits
- Define CPU and memory limits for pods
- Suitable for local development (Minikube)

### NFR-4: Security
- Non-root container execution
- Secrets properly encoded (base64)
- No sensitive data in ConfigMaps

## Technology Stack

| Component | Technology |
|-----------|-----------|
| Containerization | Docker (Docker Desktop) |
| Docker AI | Docker AI Agent (Gordon) - Optional |
| Orchestration | Kubernetes (Minikube) |
| Package Manager | Helm Charts |
| AI DevOps | kubectl-ai, Kagent |
| Application | Phase III Todo Chatbot |

## Project Structure

```
k8s/
├── helm/
│   ├── todo-backend/
│   │   ├── Chart.yaml
│   │   ├── values.yaml
│   │   └── templates/
│   │       ├── deployment.yaml
│   │       ├── service.yaml
│   │       ├── configmap.yaml
│   │       ├── secret.yaml
│   │       └── _helpers.tpl
│   └── todo-frontend/
│       ├── Chart.yaml
│       ├── values.yaml
│       └── templates/
│           ├── deployment.yaml
│           ├── service.yaml
│           ├── configmap.yaml
│           ├── secret.yaml
│           └── _helpers.tpl
├── Dockerfile.backend
├── Dockerfile.frontend
├── scripts/
│   ├── deploy.sh
│   ├── teardown.sh
│   └── build-images.sh
└── README.md
```

## Docker AI Agent (Gordon) Usage

If Docker Desktop 4.53+ with Gordon enabled:

```bash
# Get Gordon capabilities
docker ai "What can you do?"

# Build optimized Dockerfile
docker ai "Create a multi-stage Dockerfile for a Python FastAPI app"

# Debug container issues
docker ai "Why is my container failing to start?"

# Optimize image size
docker ai "How can I reduce my Docker image size?"
```

Note: If Gordon is unavailable in your region or tier, use standard Docker CLI commands.

## AI DevOps Tool Usage

### kubectl-ai Examples
```bash
# Deploy applications
kubectl-ai "deploy the todo frontend with 2 replicas"
kubectl-ai "scale the backend to handle more load"

# Troubleshoot issues
kubectl-ai "check why the pods are failing"
kubectl-ai "show me the logs from the backend pods"

# Resource management
kubectl-ai "show resource usage for all pods"
```

### Kagent Examples
```bash
# Cluster analysis
kagent "analyze the cluster health"
kagent "optimize resource allocation"

# Advanced operations
kagent "check for security vulnerabilities"
kagent "suggest improvements for the deployment"
```

## Deployment Commands

```bash
# Start Minikube
minikube start --cpus=2 --memory=4096

# Build images
docker build -f k8s/Dockerfile.backend -t todo-backend:latest ./backend
docker build -f k8s/Dockerfile.frontend -t todo-frontend:latest ./frontend

# Load images into Minikube
minikube image load todo-backend:latest
minikube image load todo-frontend:latest

# Create secrets
kubectl create secret generic todo-secrets \
  --from-literal=database-url="$DATABASE_URL" \
  --from-literal=better-auth-secret="$BETTER_AUTH_SECRET" \
  --from-literal=openai-api-key="$OPENAI_API_KEY"

# Deploy with Helm
helm install todo-backend k8s/helm/todo-backend
helm install todo-frontend k8s/helm/todo-frontend

# Access application
minikube service todo-frontend

# Check status
kubectl get pods
kubectl get services
```

## Environment Variables

### Backend Container
| Variable | Source | Description |
|----------|--------|-------------|
| DATABASE_URL | Secret | Neon PostgreSQL connection string |
| BETTER_AUTH_SECRET | Secret | JWT validation secret |
| OPENAI_API_KEY | Secret | OpenAI API key for chat |
| CORS_ORIGINS | ConfigMap | Allowed CORS origins |

### Frontend Container
| Variable | Source | Description |
|----------|--------|-------------|
| DATABASE_URL | Secret | Better Auth database connection |
| BETTER_AUTH_SECRET | Secret | Better Auth secret |
| NEXT_PUBLIC_APP_URL | ConfigMap | Frontend URL |
| NEXT_PUBLIC_API_URL | ConfigMap | Backend API URL |
