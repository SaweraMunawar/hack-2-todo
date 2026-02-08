#!/bin/bash
# Build Docker images for Todo App
# Phase IV: Local Kubernetes Deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get the root directory (parent of k8s)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"
K8S_DIR="${ROOT_DIR}/k8s"

echo -e "${YELLOW}Building Docker images for Todo App...${NC}"
echo "Root directory: ${ROOT_DIR}"

# Build backend image
echo -e "\n${YELLOW}Building backend image...${NC}"
docker build \
    -f "${K8S_DIR}/Dockerfile.backend" \
    -t todo-backend:latest \
    "${ROOT_DIR}/backend"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}Backend image built successfully!${NC}"
else
    echo -e "${RED}Failed to build backend image${NC}"
    exit 1
fi

# Build frontend image
echo -e "\n${YELLOW}Building frontend image...${NC}"

# Get environment variables or use defaults
NEXT_PUBLIC_APP_URL="${NEXT_PUBLIC_APP_URL:-http://localhost:30000}"
NEXT_PUBLIC_API_URL="${NEXT_PUBLIC_API_URL:-http://localhost:30001/api/v1}"

docker build \
    -f "${K8S_DIR}/Dockerfile.frontend" \
    --build-arg NEXT_PUBLIC_APP_URL="${NEXT_PUBLIC_APP_URL}" \
    --build-arg NEXT_PUBLIC_API_URL="${NEXT_PUBLIC_API_URL}" \
    -t todo-frontend:latest \
    "${ROOT_DIR}/frontend"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}Frontend image built successfully!${NC}"
else
    echo -e "${RED}Failed to build frontend image${NC}"
    exit 1
fi

# Show image sizes
echo -e "\n${YELLOW}Image sizes:${NC}"
docker images | grep -E "^todo-(backend|frontend)" | awk '{printf "%-20s %s\n", $1":"$2, $7$8}'

echo -e "\n${GREEN}All images built successfully!${NC}"
echo -e "\nTo load images into Minikube, run:"
echo -e "  minikube image load todo-backend:latest"
echo -e "  minikube image load todo-frontend:latest"
