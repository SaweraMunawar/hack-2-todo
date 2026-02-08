#!/bin/bash
# Deploy Todo App to Minikube
# Phase IV: Local Kubernetes Deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get the root directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"
K8S_DIR="${ROOT_DIR}/k8s"

echo -e "${YELLOW}Deploying Todo App to Minikube...${NC}"

# Check if Minikube is running
if ! minikube status | grep -q "Running"; then
    echo -e "${YELLOW}Starting Minikube...${NC}"
    minikube start --cpus=2 --memory=4096
fi

# Check if required environment variables are set
if [ -z "$DATABASE_URL" ]; then
    echo -e "${RED}ERROR: DATABASE_URL environment variable is not set${NC}"
    echo "Please set it with: export DATABASE_URL='postgresql://...'"
    exit 1
fi

if [ -z "$BETTER_AUTH_SECRET" ]; then
    echo -e "${RED}ERROR: BETTER_AUTH_SECRET environment variable is not set${NC}"
    echo "Please set it with: export BETTER_AUTH_SECRET='your-secret'"
    exit 1
fi

if [ -z "$OPENAI_API_KEY" ]; then
    echo -e "${YELLOW}WARNING: OPENAI_API_KEY is not set. Chat functionality will not work.${NC}"
    OPENAI_API_KEY="not-set"
fi

# Load images into Minikube
echo -e "\n${YELLOW}Loading images into Minikube...${NC}"
minikube image load todo-backend:latest 2>/dev/null || {
    echo -e "${YELLOW}Backend image not found locally. Building...${NC}"
    "${SCRIPT_DIR}/build-images.sh"
    minikube image load todo-backend:latest
}

minikube image load todo-frontend:latest 2>/dev/null || {
    echo -e "${YELLOW}Frontend image not found locally.${NC}"
    minikube image load todo-frontend:latest
}

# Create or update secrets
echo -e "\n${YELLOW}Creating secrets...${NC}"
kubectl delete secret todo-secrets --ignore-not-found=true
kubectl create secret generic todo-secrets \
    --from-literal=database-url="${DATABASE_URL}" \
    --from-literal=better-auth-secret="${BETTER_AUTH_SECRET}" \
    --from-literal=openai-api-key="${OPENAI_API_KEY}"

echo -e "${GREEN}Secrets created successfully!${NC}"

# Get Minikube IP for configuration
MINIKUBE_IP=$(minikube ip)
FRONTEND_URL="http://${MINIKUBE_IP}:30000"
BACKEND_URL="http://${MINIKUBE_IP}:30001"

# Deploy backend
echo -e "\n${YELLOW}Deploying backend...${NC}"
helm upgrade --install todo-backend "${K8S_DIR}/helm/todo-backend" \
    --set config.corsOrigins="${FRONTEND_URL}" \
    --set service.type=NodePort \
    --set service.nodePort=30001 \
    --wait --timeout=120s

echo -e "${GREEN}Backend deployed successfully!${NC}"

# Deploy frontend
echo -e "\n${YELLOW}Deploying frontend...${NC}"
helm upgrade --install todo-frontend "${K8S_DIR}/helm/todo-frontend" \
    --set config.appUrl="${FRONTEND_URL}" \
    --set config.apiUrl="${BACKEND_URL}/api/v1" \
    --wait --timeout=120s

echo -e "${GREEN}Frontend deployed successfully!${NC}"

# Wait for pods to be ready
echo -e "\n${YELLOW}Waiting for pods to be ready...${NC}"
kubectl wait --for=condition=ready pod -l app=todo-backend --timeout=120s
kubectl wait --for=condition=ready pod -l app=todo-frontend --timeout=120s

# Show status
echo -e "\n${BLUE}Deployment Status:${NC}"
kubectl get pods -l "app in (todo-backend, todo-frontend)"
echo ""
kubectl get services -l "app.kubernetes.io/name in (todo-backend, todo-frontend)"

# Show access information
echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "\nFrontend URL: ${BLUE}${FRONTEND_URL}${NC}"
echo -e "Backend API:  ${BLUE}${BACKEND_URL}/api/v1${NC}"
echo -e "\nTo open in browser, run:"
echo -e "  ${YELLOW}minikube service todo-frontend${NC}"
echo -e "\nTo view logs:"
echo -e "  ${YELLOW}kubectl logs -l app=todo-backend -f${NC}"
echo -e "  ${YELLOW}kubectl logs -l app=todo-frontend -f${NC}"
