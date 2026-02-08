# Phase IV: Docker Specification

## Backend Dockerfile

### Base Image
- Python 3.13-slim for production
- Multi-stage build for smaller image size

### Build Stage
1. Install UV for Python dependency management
2. Copy pyproject.toml and uv.lock
3. Install dependencies to virtual environment
4. Copy source code

### Production Stage
1. Copy virtual environment from build stage
2. Copy source code
3. Create non-root user (appuser)
4. Expose port 8000
5. Set environment variables
6. Run with uvicorn

### Health Check
- Endpoint: `/api/v1/health`
- Interval: 30s
- Timeout: 10s
- Retries: 3

### Dockerfile Structure
```dockerfile
# Build stage
FROM python:3.13-slim AS builder
WORKDIR /app
# Install UV and dependencies
# Copy and install requirements

# Production stage
FROM python:3.13-slim AS production
WORKDIR /app
# Copy from builder
# Create non-root user
# Set permissions
# Expose port
# Health check
# CMD
```

## Frontend Dockerfile

### Base Image
- Node 22-alpine for smaller image
- Multi-stage build

### Dependencies Stage
1. Install pnpm
2. Copy package.json and pnpm-lock.yaml
3. Install dependencies

### Build Stage
1. Copy dependencies from deps stage
2. Copy source code
3. Set build-time environment variables
4. Run `pnpm build`

### Production Stage
1. Copy standalone build from builder
2. Create non-root user (nextjs)
3. Expose port 3000
4. Run with `node server.js`

### Health Check
- Endpoint: `/` (Next.js serves the app)
- Interval: 30s
- Timeout: 10s
- Retries: 3

### Next.js Configuration
Must enable standalone output in next.config.ts:
```typescript
const nextConfig = {
  output: 'standalone',
};
```

## Image Naming Convention

| Image | Tag Pattern | Example |
|-------|-------------|---------|
| Backend | todo-backend:{version} | todo-backend:1.0.0 |
| Frontend | todo-frontend:{version} | todo-frontend:1.0.0 |
| Development | {name}:latest | todo-backend:latest |

## Build Commands

```bash
# Backend
docker build -f k8s/Dockerfile.backend -t todo-backend:latest ./backend

# Frontend
docker build -f k8s/Dockerfile.frontend -t todo-frontend:latest ./frontend

# With version tag
docker build -f k8s/Dockerfile.backend -t todo-backend:1.0.0 ./backend
docker build -f k8s/Dockerfile.frontend -t todo-frontend:1.0.0 ./frontend
```

## Environment Variables at Build Time

### Frontend Build Args
| ARG | Description |
|-----|-------------|
| NEXT_PUBLIC_APP_URL | Application URL (for auth callbacks) |
| NEXT_PUBLIC_API_URL | Backend API URL |

```bash
docker build \
  --build-arg NEXT_PUBLIC_APP_URL=http://localhost:3000 \
  --build-arg NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1 \
  -f k8s/Dockerfile.frontend -t todo-frontend:latest ./frontend
```

## Security Requirements

1. **Non-root user**: Both containers run as non-root
2. **Read-only filesystem**: Where possible
3. **No secrets in image**: All secrets via environment variables
4. **Minimal base image**: Using slim/alpine variants
5. **Multi-stage builds**: No build tools in production image
