# Todo App Evolution - Hackathon II

A spec-driven development project transforming a simple console app into a cloud-native AI-powered system.

## Current Phase: Phase II - Full-Stack Web Application

Multi-user web application with persistent storage, JWT authentication, and RESTful API.

## Quick Start

### Prerequisites
- Python 3.13+
- Node.js 22+
- [UV package manager](https://docs.astral.sh/uv/)
- [pnpm](https://pnpm.io/)
- [Neon PostgreSQL](https://neon.tech/) database

### Phase I - Console App

```bash
# Sync dependencies
uv sync

# Run the application
uv run python -m todo

# Run tests
uv run pytest tests/
```

### Phase II - Full-Stack Web App

#### Backend (FastAPI)

```bash
cd backend

# Copy and configure environment
cp .env.example .env
# Edit .env with your DATABASE_URL, BETTER_AUTH_SECRET, CORS_ORIGINS

# Install dependencies
uv sync

# Run tests
uv run pytest tests/ -v

# Start development server
uv run uvicorn todo_api.main:app --reload --port 8000
```

#### Frontend (Next.js + Better Auth)

```bash
cd frontend

# Copy and configure environment
cp .env.example .env
# Edit .env with your DATABASE_URL, BETTER_AUTH_SECRET, app URLs

# Install dependencies
pnpm install

# Generate Better Auth tables (first time only)
pnpm dlx @better-auth/cli generate
pnpm dlx @better-auth/cli migrate

# Start development server
pnpm dev
```

#### Running Both Services

```bash
# Terminal 1 - Backend
cd backend && uv run uvicorn todo_api.main:app --reload --port 8000

# Terminal 2 - Frontend
cd frontend && pnpm dev
```

Visit http://localhost:3000 to use the application.

## Features

### Phase I - Console App

| Feature | Description | Status |
|---------|-------------|--------|
| Add Task | Create new tasks with title and description | Done |
| View Tasks | Display all tasks with status | Done |
| Update Task | Modify existing task details | Done |
| Delete Task | Remove tasks with confirmation | Done |
| Mark Complete | Toggle task completion status | Done |

### Phase II - Web Application

| Feature | Description | Status |
|---------|-------------|--------|
| User Registration | Sign up with email/password via Better Auth | Done |
| User Login/Logout | Session management with JWT tokens | Done |
| Task CRUD | Create, read, update, delete tasks via REST API | Done |
| Task Completion | Toggle task completion status | Done |
| Task Filtering | Filter by All, Active, Completed | Done |
| Data Isolation | Users can only access their own tasks | Done |
| JWT Authentication | Shared secret (HS256) between frontend and backend | Done |
| Responsive UI | Mobile-friendly Tailwind CSS design | Done |

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 16, React 19, Tailwind CSS |
| Auth | Better Auth with JWT plugin |
| Backend | FastAPI, SQLModel, PyJWT |
| Database | Neon Serverless PostgreSQL |
| Package Mgmt | pnpm (frontend), UV (backend) |

## Project Structure

```
todo-app/
├── specs/
│   ├── phase1/                 # Phase I specifications
│   └── phase2/                 # Phase II specifications
│       ├── requirements.md
│       ├── data-model.md
│       ├── api-spec.md
│       ├── auth-spec.md
│       ├── database-spec.md
│       ├── frontend-spec.md
│       └── acceptance-criteria.md
├── src/todo/                   # Phase I console app
├── backend/                    # FastAPI backend
│   ├── src/todo_api/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── routers/tasks.py
│   │   └── auth/jwt.py
│   └── tests/
├── frontend/                   # Next.js frontend
│   ├── app/
│   │   ├── api/auth/[...all]/
│   │   ├── login/
│   │   ├── register/
│   │   └── tasks/
│   ├── components/
│   │   ├── auth/
│   │   ├── tasks/
│   │   └── layout/
│   └── lib/
│       ├── auth.ts
│       ├── auth-client.ts
│       └── api.ts
├── tests/                      # Phase I tests
├── CLAUDE.md
├── constitution.md
└── README.md
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/v1/health | Health check |
| GET | /api/v1/tasks | List tasks (with filters) |
| POST | /api/v1/tasks | Create task |
| GET | /api/v1/tasks/{id} | Get single task |
| PATCH | /api/v1/tasks/{id} | Update task |
| DELETE | /api/v1/tasks/{id} | Delete task |
| POST | /api/v1/tasks/{id}/toggle | Toggle completion |

All task endpoints require JWT authentication via `Authorization: Bearer <token>` header.

## Security

- Passwords hashed by Better Auth (Argon2/bcrypt)
- JWT validation via shared secret (HS256)
- SQL injection prevention via SQLModel ORM
- XSS prevention via React escaping
- CORS configured for frontend origin only
- 404 returned for unauthorized resource access (prevents enumeration)

## Development Approach

This project uses **spec-driven development**:

1. **Write specifications** - Define features in markdown
2. **Generate code** - Use Claude Code to implement specs
3. **Validate** - Test against acceptance criteria
4. **Refine** - Iterate on specs until correct

See [CLAUDE.md](CLAUDE.md) for detailed development instructions.

## Roadmap

| Phase | Description | Status |
|-------|-------------|--------|
| I | Console App (In-Memory) | Complete |
| II | Web App (FastAPI/Next.js) | Complete |
| III | AI Chatbot (MCP Tools) | Planned |
| IV | Kubernetes Deployment | Planned |
| V | Cloud-Native Architecture | Planned |

## License

MIT License - See LICENSE file for details.
