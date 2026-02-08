# Phase IV: Helm Charts Specification

## Chart Structure

### todo-backend Chart

```
helm/todo-backend/
├── Chart.yaml           # Chart metadata
├── values.yaml          # Default configuration
└── templates/
    ├── _helpers.tpl     # Template helpers
    ├── deployment.yaml  # Kubernetes Deployment
    ├── service.yaml     # Kubernetes Service
    ├── configmap.yaml   # ConfigMap for non-sensitive config
    └── secret.yaml      # Secret for sensitive data (optional)
```

### todo-frontend Chart

```
helm/todo-frontend/
├── Chart.yaml           # Chart metadata
├── values.yaml          # Default configuration
└── templates/
    ├── _helpers.tpl     # Template helpers
    ├── deployment.yaml  # Kubernetes Deployment
    ├── service.yaml     # Kubernetes Service
    ├── configmap.yaml   # ConfigMap for non-sensitive config
    └── secret.yaml      # Secret for sensitive data (optional)
```

## Chart.yaml Specification

### Backend Chart.yaml
```yaml
apiVersion: v2
name: todo-backend
description: FastAPI backend for Todo AI Chatbot
type: application
version: 1.0.0
appVersion: "1.0.0"
```

### Frontend Chart.yaml
```yaml
apiVersion: v2
name: todo-frontend
description: Next.js frontend for Todo AI Chatbot
type: application
version: 1.0.0
appVersion: "1.0.0"
```

## values.yaml Specification

### Backend values.yaml
```yaml
replicaCount: 1

image:
  repository: todo-backend
  tag: latest
  pullPolicy: IfNotPresent

service:
  type: ClusterIP
  port: 8000
  targetPort: 8000

resources:
  limits:
    cpu: 500m
    memory: 512Mi
  requests:
    cpu: 100m
    memory: 256Mi

config:
  corsOrigins: "http://localhost:3000"

# External secrets (created separately)
externalSecrets:
  name: todo-secrets

# Health checks
livenessProbe:
  path: /api/v1/health
  initialDelaySeconds: 10
  periodSeconds: 30
  timeoutSeconds: 10

readinessProbe:
  path: /api/v1/health
  initialDelaySeconds: 5
  periodSeconds: 10
  timeoutSeconds: 5
```

### Frontend values.yaml
```yaml
replicaCount: 1

image:
  repository: todo-frontend
  tag: latest
  pullPolicy: IfNotPresent

service:
  type: NodePort
  port: 3000
  targetPort: 3000
  nodePort: 30000

resources:
  limits:
    cpu: 500m
    memory: 512Mi
  requests:
    cpu: 100m
    memory: 256Mi

config:
  appUrl: "http://localhost:30000"
  apiUrl: "http://todo-backend:8000/api/v1"

# External secrets (created separately)
externalSecrets:
  name: todo-secrets

# Health checks
livenessProbe:
  path: /
  initialDelaySeconds: 15
  periodSeconds: 30
  timeoutSeconds: 10

readinessProbe:
  path: /
  initialDelaySeconds: 10
  periodSeconds: 10
  timeoutSeconds: 5
```

## Template Specifications

### Deployment Template Requirements

1. **Pod Labels**: Include app name, version, and chart info
2. **Container Spec**:
   - Image from values
   - Environment variables from ConfigMap and Secret
   - Resource limits and requests
   - Liveness and readiness probes
   - Security context (non-root)
3. **Pod Security Context**:
   - runAsNonRoot: true
   - runAsUser: 1000

### Service Template Requirements

1. **Backend Service**:
   - Type: ClusterIP (internal only)
   - Port: 8000
   - Selector matching deployment labels

2. **Frontend Service**:
   - Type: NodePort (external access for Minikube)
   - Port: 3000
   - NodePort: 30000 (configurable)
   - Selector matching deployment labels

### ConfigMap Template Requirements

1. **Backend ConfigMap**:
   - CORS_ORIGINS

2. **Frontend ConfigMap**:
   - NEXT_PUBLIC_APP_URL
   - NEXT_PUBLIC_API_URL

### Secret Management

Secrets are created externally via kubectl for better security:

```bash
kubectl create secret generic todo-secrets \
  --from-literal=database-url="$DATABASE_URL" \
  --from-literal=better-auth-secret="$BETTER_AUTH_SECRET" \
  --from-literal=openai-api-key="$OPENAI_API_KEY"
```

Helm charts reference this external secret by name.

## Helm Commands

```bash
# Install backend
helm install todo-backend ./k8s/helm/todo-backend

# Install frontend
helm install todo-frontend ./k8s/helm/todo-frontend

# Install with custom values
helm install todo-backend ./k8s/helm/todo-backend \
  --set replicaCount=2 \
  --set resources.limits.memory=1Gi

# Upgrade deployment
helm upgrade todo-backend ./k8s/helm/todo-backend

# Uninstall
helm uninstall todo-backend
helm uninstall todo-frontend

# List releases
helm list

# Check status
helm status todo-backend
```

## AI-Assisted Chart Generation

Using kubectl-ai or kagent to generate/modify charts:

```bash
# Generate deployment with kubectl-ai
kubectl-ai "create a deployment for todo-backend with 2 replicas"

# Scale using AI
kubectl-ai "scale todo-frontend to 3 replicas"

# Troubleshoot with kagent
kagent "analyze why todo-backend pods are not ready"
```
