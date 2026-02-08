# Claude Code Instructions

## Project Overview
This is the "Evolution of Todo" hackathon project - a spec-driven development exercise building a todo application that evolves from console to cloud-native.

**Current Phase**: Phase V - Cloud Native Deployment (Phases I, II, III & IV complete)

## Spec-Driven Development Rules

### MUST Follow
1. **Read specifications first** - Specs are in `/specs/phase{N}/`
2. **Generate code from specs** - Do not write code manually
3. **Use UV for backend** - All Python commands use `uv run`
4. **Use pnpm for frontend** - All Node commands use `pnpm`
5. **Validate against acceptance criteria** - See `specs/phase{N}/acceptance-criteria.md`

### MUST NOT Do
- Write code without reading the relevant specification
- Use pip directly (use UV instead)
- Use npm directly (use pnpm instead)
- Add features not in specifications
- Skip validation steps
- Expose sensitive data (passwords, tokens) in logs

## Technology Stack

### Authentication
- **Better Auth** - Handles user registration, login, session management
- **JWT Plugin** - Issues JWT tokens for API authorization
- **Shared Secret (HS256)** - FastAPI validates JWTs using BETTER_AUTH_SECRET

### Backend (FastAPI)
- **SQLModel** - ORM for task CRUD and chat persistence
- **PyJWT** - Validates JWTs from Better Auth via shared secret
- **Neon PostgreSQL** - Serverless database
- **OpenAI Agents SDK** - AI agent for chat (Phase III)
- **MCP SDK** - Model Context Protocol tools for task operations (Phase III)

### Frontend (Next.js)
- **Better Auth Client** - React hooks for auth state
- **Tailwind CSS** - Styling
- **App Router** - File-based routing
- **Chat UI** - Conversational interface for task management (Phase III)

### Kubernetes (Phase IV)
- **Docker** - Container images for frontend and backend
- **Minikube** - Local Kubernetes cluster
- **Helm Charts** - Package manager for K8s deployments
- **kubectl-ai / Kagent** - AI-assisted Kubernetes operations

### Cloud Native (Phase V)
- **Kafka/Redpanda** - Event streaming
- **Dapr** - Distributed application runtime
- **DOKS/GKE/AKS** - Cloud Kubernetes
- **GitHub Actions** - CI/CD pipeline

## Project Structure

```
todo-app/
├── specs/
│   ├── phase1/                 # Phase I specs
│   ├── phase2/                 # Phase II specs
│   ├── phase3/                 # Phase III specs (AI Chatbot)
│   │   ├── requirements.md
│   │   ├── data-model.md
│   │   ├── api-spec.md
│   │   ├── mcp-spec.md
│   │   ├── frontend-spec.md
│   │   └── acceptance-criteria.md
│   ├── phase4/                 # Phase IV specs (Kubernetes)
│   │   ├── requirements.md
│   │   ├── docker-spec.md
│   │   ├── helm-spec.md
│   │   └── acceptance-criteria.md
│   └── phase5/                 # Phase V specs (Cloud Deployment)
│       ├── requirements.md
│       ├── data-model.md
│       ├── api-spec.md
│       ├── kafka-spec.md
│       ├── dapr-spec.md
│       └── acceptance-criteria.md
├── backend/                    # FastAPI backend
│   ├── src/todo_api/
│   │   ├── main.py             # FastAPI app
│   │   ├── config.py           # Settings
│   │   ├── database.py         # SQLModel setup
│   │   ├── models.py           # Task, Conversation, Message models
│   │   ├── routers/
│   │   │   ├── tasks.py        # Task CRUD routes
│   │   │   └── chat.py         # Chat endpoint (Phase III)
│   │   ├── auth/
│   │   │   └── jwt.py          # JWT validation
│   │   └── mcp/
│   │       └── tools.py        # MCP task tools (Phase III)
│   ├── tests/
│   ├── pyproject.toml
│   └── .env.example
├── frontend/                   # Next.js + Better Auth
│   ├── app/
│   │   ├── api/auth/[...all]/  # Better Auth handler
│   │   ├── login/
│   │   ├── register/
│   │   ├── tasks/
│   │   └── chat/               # Chat page (Phase III)
│   ├── components/
│   │   ├── auth/
│   │   ├── tasks/
│   │   ├── chat/               # Chat components (Phase III)
│   │   └── layout/
│   ├── lib/
│   │   ├── auth.ts
│   │   ├── auth-client.ts
│   │   └── api.ts
│   ├── types/
│   ├── package.json
│   └── .env.example
├── k8s/                        # Kubernetes configs (Phase IV)
│   ├── Dockerfile.backend      # Backend multi-stage Dockerfile
│   ├── Dockerfile.frontend     # Frontend multi-stage Dockerfile
│   ├── helm/
│   │   ├── todo-backend/       # Backend Helm chart
│   │   │   ├── Chart.yaml
│   │   │   ├── values.yaml
│   │   │   └── templates/
│   │   └── todo-frontend/      # Frontend Helm chart
│   │       ├── Chart.yaml
│   │       ├── values.yaml
│   │       └── templates/
│   ├── scripts/
│   │   ├── build-images.sh     # Build Docker images
│   │   ├── deploy.sh           # Deploy to Minikube
│   │   └── teardown.sh         # Remove deployment
│   └── README.md               # Kubernetes deployment guide
├── dapr/                       # Dapr configs (Phase V)
│   ├── components/
│   │   ├── kafka-pubsub.yaml   # Kafka pub/sub (local)
│   │   ├── kafka-pubsub-cloud.yaml  # Kafka pub/sub (cloud)
│   │   ├── statestore.yaml     # PostgreSQL state store
│   │   ├── reminder-cron.yaml  # Cron binding for reminders
│   │   └── secrets.yaml        # K8s secret store
│   ├── config/
│   │   └── config.yaml         # Dapr configuration
│   ├── subscriptions/          # Dapr subscriptions
│   └── README.md               # Dapr setup guide
├── .github/workflows/          # CI/CD (Phase V)
│   ├── ci.yml                  # Continuous Integration
│   └── deploy.yml              # Continuous Deployment
├── docker-compose.redpanda.yml # Local Kafka (Redpanda)
├── src/todo/                   # Phase I (preserved)
├── CLAUDE.md                   # This file
├── constitution.md             # Project principles
└── README.md
```

## Key Commands

### Backend (FastAPI)

```bash
cd backend

# Install dependencies
uv sync

# Run development server
uv run uvicorn todo_api.main:app --reload --port 8000

# Run tests
uv run pytest

# Format code
uv run ruff format src/

# Lint code
uv run ruff check src/
```

### Frontend (Next.js + Better Auth)

```bash
cd frontend

# Install dependencies
pnpm install

# Generate Better Auth tables
pnpm dlx @better-auth/cli generate
pnpm dlx @better-auth/cli migrate

# Run development server
pnpm dev

# Build for production
pnpm build

# Run linting
pnpm lint
```

### Kubernetes (Phase IV)

```bash
# Build Docker images
./k8s/scripts/build-images.sh

# Deploy to Minikube
./k8s/scripts/deploy.sh

# Teardown
./k8s/scripts/teardown.sh

# Manual Helm commands
helm install todo-backend k8s/helm/todo-backend
helm install todo-frontend k8s/helm/todo-frontend
helm uninstall todo-backend todo-frontend
```

### Kafka & Dapr (Phase V)

```bash
# Start local Kafka (Redpanda)
docker compose -f docker-compose.redpanda.yml up -d

# View Redpanda Console
open http://localhost:8080

# Run backend with Dapr sidecar
dapr run --app-id todo-backend --app-port 8000 --dapr-http-port 3500 \
  --resources-path ./dapr/components \
  -- uv run uvicorn todo_api.main:app --host 0.0.0.0 --port 8000

# Initialize Dapr on Kubernetes
dapr init -k

# Apply Dapr components
kubectl apply -f dapr/components/
kubectl apply -f dapr/config/
kubectl apply -f dapr/subscriptions/
```

### Phase I Console App (preserved)

```bash
uv run python -m todo
```

## Feature Checklist

### Phase I - Console App: COMPLETE
All 5 basic features implemented and tested (60/60 tests pass).

### Phase II - Web App: COMPLETE
All CRUD, auth, data isolation implemented and tested (15/15 tests pass).

### Phase III - AI Chatbot: COMPLETE

| Feature | Spec Reference | Status |
|---------|----------------|--------|
| Conversation model | phase3/data-model.md | ✅ |
| Message model | phase3/data-model.md | ✅ |
| Chat endpoint | phase3/api-spec.md | ✅ |
| MCP tools (add, list, complete, delete, update) | phase3/mcp-spec.md | ✅ |
| OpenAI Agent integration | phase3/requirements.md | ✅ |
| Chat frontend | phase3/frontend-spec.md | ✅ |
| Conversation list | phase3/frontend-spec.md | ✅ |
| Conversation persistence | phase3/acceptance-criteria.md | ✅ |

### Phase IV - Kubernetes: COMPLETE

| Feature | Spec Reference | Status |
|---------|----------------|--------|
| Backend Dockerfile | phase4/docker-spec.md | ✅ |
| Frontend Dockerfile | phase4/docker-spec.md | ✅ |
| Backend Helm chart | phase4/helm-spec.md | ✅ |
| Frontend Helm chart | phase4/helm-spec.md | ✅ |
| Deployment scripts | phase4/requirements.md | ✅ |
| Minikube deployment | phase4/acceptance-criteria.md | ⬜ (test pending) |

### Phase V - Cloud Deployment: IN PROGRESS

| Feature | Spec Reference | Status |
|---------|----------------|--------|
| Priority feature | phase5/requirements.md | ✅ |
| Tags feature | phase5/requirements.md | ✅ |
| Search/Filter/Sort | phase5/requirements.md | ✅ |
| Due dates & reminders | phase5/requirements.md | ✅ |
| Recurring tasks | phase5/requirements.md | ✅ |
| Advanced MCP tools | phase5/requirements.md | ✅ |
| Backend event publishing | phase5/kafka-spec.md | ✅ |
| Kafka/Redpanda docker-compose | phase5/kafka-spec.md | ✅ |
| Dapr components | phase5/dapr-spec.md | ✅ |
| GitHub Actions CI/CD | phase5/requirements.md | ✅ |
| Frontend Phase V UI | phase5/requirements.md | ✅ |
| Cloud K8s deployment | phase5/requirements.md | ⬜ (deployment pending) |

## Environment Variables

### Frontend (.env)
```bash
DATABASE_URL=postgresql://user:password@host/dbname?sslmode=require
BETTER_AUTH_SECRET=<generated-32-char-secret>
NEXT_PUBLIC_APP_URL=http://localhost:3000
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

### Backend (.env)
```bash
DATABASE_URL=postgresql://user:password@host/dbname?sslmode=require
BETTER_AUTH_SECRET=<same-32-char-secret-as-frontend>
CORS_ORIGINS=http://localhost:3000
OPENAI_API_KEY=sk-...  # Phase III
```

### Kubernetes (Phase IV)
```bash
# Set before running deploy.sh
export DATABASE_URL="postgresql://..."
export BETTER_AUTH_SECRET="your-secret"
export OPENAI_API_KEY="sk-..."
```

### Phase V (Additional)
```bash
KAFKA_BOOTSTRAP_SERVERS=your-cluster.cloud.redpanda.com:9092
KAFKA_USERNAME=your-username
KAFKA_PASSWORD=your-password
DAPR_HTTP_PORT=3500
```

## Security Requirements

- Passwords hashed by Better Auth (Argon2/bcrypt)
- JWT validated via shared secret (HS256)
- SQL injection prevented via SQLModel
- XSS prevented via React escaping
- CORS configured for frontend origin only
- 404 returned for unauthorized resource access (not 403)
- OpenAI API key stored in environment variables only
- Kubernetes secrets for sensitive data (not ConfigMaps)
- Non-root containers for security
