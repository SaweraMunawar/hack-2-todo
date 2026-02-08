# Phase IV: Local Kubernetes Deployment

Deploy the Todo AI Chatbot on a local Kubernetes cluster using Minikube and Helm Charts.

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) or Docker Engine
- [Minikube](https://minikube.sigs.k8s.io/docs/start/)
- [kubectl](https://kubernetes.io/docs/tasks/tools/)
- [Helm](https://helm.sh/docs/intro/install/)

### Optional AI Tools

- [kubectl-ai](https://github.com/sozercan/kubectl-ai) - AI-assisted kubectl
- [Kagent](https://github.com/kagent-dev/kagent) - AI Kubernetes agent
- Docker AI Agent (Gordon) - Available in Docker Desktop 4.53+

## Quick Start

### 1. Set Environment Variables

```bash
# Required
export DATABASE_URL="postgresql://user:password@host/dbname?sslmode=require"
export BETTER_AUTH_SECRET="your-32-char-secret"

# Optional (for chat functionality)
export OPENAI_API_KEY="sk-..."
```

### 2. Build Images

```bash
./k8s/scripts/build-images.sh
```

### 3. Deploy to Minikube

```bash
./k8s/scripts/deploy.sh
```

### 4. Access the Application

```bash
minikube service todo-frontend
```

## Manual Deployment

### Start Minikube

```bash
minikube start --cpus=2 --memory=4096
```

### Build and Load Images

```bash
# Build images
docker build -f k8s/Dockerfile.backend -t todo-backend:latest ./backend
docker build -f k8s/Dockerfile.frontend -t todo-frontend:latest ./frontend

# Load into Minikube
minikube image load todo-backend:latest
minikube image load todo-frontend:latest
```

### Create Secrets

```bash
kubectl create secret generic todo-secrets \
  --from-literal=database-url="$DATABASE_URL" \
  --from-literal=better-auth-secret="$BETTER_AUTH_SECRET" \
  --from-literal=openai-api-key="$OPENAI_API_KEY"
```

### Deploy with Helm

```bash
# Deploy backend
helm install todo-backend k8s/helm/todo-backend

# Deploy frontend
helm install todo-frontend k8s/helm/todo-frontend
```

### Check Status

```bash
kubectl get pods
kubectl get services
```

## Teardown

```bash
./k8s/scripts/teardown.sh

# Optionally stop Minikube
minikube stop

# Or delete the cluster entirely
minikube delete
```

## Project Structure

```
k8s/
├── Dockerfile.backend      # Backend multi-stage build
├── Dockerfile.frontend     # Frontend multi-stage build
├── helm/
│   ├── todo-backend/       # Backend Helm chart
│   │   ├── Chart.yaml
│   │   ├── values.yaml
│   │   └── templates/
│   └── todo-frontend/      # Frontend Helm chart
│       ├── Chart.yaml
│       ├── values.yaml
│       └── templates/
├── scripts/
│   ├── build-images.sh     # Build Docker images
│   ├── deploy.sh           # Deploy to Minikube
│   └── teardown.sh         # Remove deployment
└── README.md               # This file
```

## Configuration

### Backend values.yaml

| Parameter | Description | Default |
|-----------|-------------|---------|
| replicaCount | Number of replicas | 1 |
| image.repository | Docker image name | todo-backend |
| image.tag | Docker image tag | latest |
| service.type | Kubernetes service type | ClusterIP |
| resources.limits.memory | Memory limit | 512Mi |
| config.corsOrigins | Allowed CORS origins | http://localhost:30000 |

### Frontend values.yaml

| Parameter | Description | Default |
|-----------|-------------|---------|
| replicaCount | Number of replicas | 1 |
| image.repository | Docker image name | todo-frontend |
| image.tag | Docker image tag | latest |
| service.type | Kubernetes service type | NodePort |
| service.nodePort | External port | 30000 |
| config.apiUrl | Backend API URL | http://todo-backend:8000/api/v1 |

## AI-Assisted Operations

### Using kubectl-ai

```bash
# Deploy with custom replicas
kubectl-ai "scale todo-backend to 2 replicas"

# Check pod issues
kubectl-ai "why are the todo-frontend pods not ready"

# View resource usage
kubectl-ai "show resource usage for all pods"
```

### Using Kagent

```bash
# Analyze cluster
kagent "analyze the health of the todo deployment"

# Optimize resources
kagent "suggest resource limits for todo-backend"
```

### Using Docker AI (Gordon)

```bash
# Debug containers
docker ai "why is my todo-backend container failing"

# Optimize Dockerfile
docker ai "how can I reduce the todo-frontend image size"
```

## Troubleshooting

### Pods Not Starting

```bash
# Check pod status
kubectl describe pod -l app=todo-backend

# Check logs
kubectl logs -l app=todo-backend

# Check events
kubectl get events --sort-by=.metadata.creationTimestamp
```

### Image Pull Errors

```bash
# Verify images are loaded in Minikube
minikube image ls | grep todo

# Reload images
minikube image load todo-backend:latest
minikube image load todo-frontend:latest
```

### Service Connection Issues

```bash
# Check service endpoints
kubectl get endpoints

# Test backend health
kubectl exec -it $(kubectl get pod -l app=todo-backend -o jsonpath='{.items[0].metadata.name}') -- curl localhost:8000/api/v1/health
```

### Secret Issues

```bash
# Verify secrets exist
kubectl get secrets

# Check secret values (base64 encoded)
kubectl get secret todo-secrets -o yaml
```

## Health Checks

Both containers include health checks:

- **Backend**: `GET /api/v1/health` - Returns `{"status": "healthy"}`
- **Frontend**: `GET /` - Returns the Next.js app

Kubernetes probes are configured:
- **Liveness**: Restart container if unhealthy
- **Readiness**: Remove from service if not ready

## Security

- Both containers run as non-root users
- Secrets stored in Kubernetes Secrets (not ConfigMaps)
- Resource limits prevent container escape
- No sensitive data baked into images
