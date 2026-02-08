# Phase IV: Acceptance Criteria

## AC-1: Dockerfiles

- [ ] Backend Dockerfile builds successfully
- [ ] Frontend Dockerfile builds successfully
- [ ] Images use multi-stage builds
- [ ] Images run as non-root user
- [ ] Backend container starts and responds to health check at `/api/v1/health`
- [ ] Frontend container starts and serves pages
- [ ] Backend image size < 500MB
- [ ] Frontend image size < 500MB

## AC-2: Helm Charts

- [ ] Backend Helm chart installs without errors
- [ ] Frontend Helm chart installs without errors
- [ ] Chart.yaml contains valid metadata
- [ ] values.yaml configures all environment variables
- [ ] Templates render correctly (`helm template` succeeds)
- [ ] ConfigMaps contain non-sensitive configuration only
- [ ] External secrets referenced correctly

## AC-3: Kubernetes Resources

- [ ] Backend Deployment creates pods successfully
- [ ] Frontend Deployment creates pods successfully
- [ ] Backend Service routes traffic to pods
- [ ] Frontend Service exposes NodePort for external access
- [ ] ConfigMaps created with correct values
- [ ] Secrets contain all required credentials

## AC-4: Health Checks

- [ ] Backend liveness probe passes
- [ ] Backend readiness probe passes
- [ ] Frontend liveness probe passes
- [ ] Frontend readiness probe passes
- [ ] Pods restart automatically on health check failure

## AC-5: Minikube Deployment

- [ ] `minikube start` initializes cluster
- [ ] Images load into Minikube successfully
- [ ] Helm charts deploy without errors
- [ ] All pods reach Running state
- [ ] `minikube service todo-frontend` opens the application
- [ ] Frontend can communicate with backend (API calls work)
- [ ] Chat functionality works end-to-end
- [ ] Task CRUD works through both Tasks page and Chat

## AC-6: Security

- [ ] Containers run as non-root user (UID 1000)
- [ ] Secrets not exposed in logs or ConfigMaps
- [ ] Resource limits defined for all containers
- [ ] No sensitive data in Docker images

## AC-7: Scripts and Automation

- [ ] `build-images.sh` builds both images
- [ ] `deploy.sh` deploys full stack to Minikube
- [ ] `teardown.sh` removes all resources cleanly
- [ ] Scripts are idempotent (can run multiple times)

## AC-8: Documentation

- [ ] README with complete setup instructions
- [ ] Prerequisites listed (Docker, Minikube, Helm, kubectl)
- [ ] Deployment commands documented
- [ ] Teardown commands documented
- [ ] Troubleshooting guide included
- [ ] AI tool usage examples (kubectl-ai, kagent)

## Test Scenarios

### TS-1: Fresh Deployment

1. Start with no Minikube cluster
2. Run `minikube start`
3. Run `./k8s/scripts/build-images.sh`
4. Run `./k8s/scripts/deploy.sh`
5. Wait for pods to be ready
6. Access frontend via `minikube service todo-frontend`
7. Verify login/register works
8. Verify task creation works
9. Verify chat functionality works

### TS-2: Restart Resilience

1. Deploy full stack
2. Run `kubectl delete pod -l app=todo-backend`
3. Wait for pod to restart
4. Verify application still works
5. Verify data persists (tasks still exist)

### TS-3: Resource Constraints

1. Deploy with default resources
2. Check pod resource usage: `kubectl top pods`
3. Verify pods stay within limits
4. No OOMKilled events

### TS-4: Health Check Recovery

1. Deploy full stack
2. Simulate backend failure (e.g., kill process)
3. Observe Kubernetes restart the container
4. Verify application recovers automatically

### TS-5: Clean Teardown

1. Deploy full stack
2. Run `./k8s/scripts/teardown.sh`
3. Verify all resources removed: `kubectl get all`
4. Verify secrets removed: `kubectl get secrets`
5. Run `minikube stop` or `minikube delete`

## Verification Commands

```bash
# Check all resources
kubectl get all

# Check pod status
kubectl get pods -o wide

# Check pod logs
kubectl logs -l app=todo-backend
kubectl logs -l app=todo-frontend

# Check health endpoints
kubectl exec -it <backend-pod> -- curl localhost:8000/api/v1/health

# Check secrets exist
kubectl get secrets

# Check configmaps
kubectl get configmaps

# Describe pod for events
kubectl describe pod <pod-name>

# Check Helm releases
helm list

# Test with AI tools
kubectl-ai "show the status of all todo pods"
kagent "analyze the health of the todo deployment"
```
