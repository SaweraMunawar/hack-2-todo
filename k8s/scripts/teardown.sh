#!/bin/bash
# Teardown Todo App from Minikube
# Phase IV: Local Kubernetes Deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Tearing down Todo App from Kubernetes...${NC}"

# Uninstall Helm releases
echo -e "\n${YELLOW}Uninstalling Helm releases...${NC}"
helm uninstall todo-frontend --ignore-not-found 2>/dev/null || true
helm uninstall todo-backend --ignore-not-found 2>/dev/null || true

# Delete secrets
echo -e "\n${YELLOW}Deleting secrets...${NC}"
kubectl delete secret todo-secrets --ignore-not-found=true

# Delete any remaining resources with our labels
echo -e "\n${YELLOW}Cleaning up remaining resources...${NC}"
kubectl delete all -l "app.kubernetes.io/name in (todo-backend, todo-frontend)" --ignore-not-found=true
kubectl delete configmap -l "app.kubernetes.io/name in (todo-backend, todo-frontend)" --ignore-not-found=true

# Show remaining resources
echo -e "\n${YELLOW}Remaining resources:${NC}"
kubectl get all 2>/dev/null || echo "No resources found"

echo -e "\n${GREEN}Teardown complete!${NC}"
echo -e "\nTo also stop Minikube, run:"
echo -e "  ${YELLOW}minikube stop${NC}"
echo -e "\nTo delete Minikube cluster entirely, run:"
echo -e "  ${YELLOW}minikube delete${NC}"
