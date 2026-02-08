# Phase II Requirements Specification

## Document Information
- **Phase**: II - Todo Full-Stack Web Application
- **Version**: 2.0.0
- **Status**: Final

---

## 1. Overview

### 1.1 Objective
Transform the Phase I console-based Todo application into a modern, secure, multi-user full-stack web application with persistent storage and JWT-based authentication via Better Auth.

### 1.2 Core Principles
- Spec-driven development using GitHub Spec-Kit + Claude Code
- Monorepo architecture with single shared context
- Stateless authentication using Better Auth + JWT plugin
- Strict user data isolation
- Clear separation of frontend, backend, and specifications

---

## 2. Functional Requirements

### 2.1 User Management
| ID | Requirement | Priority |
|----|-------------|----------|
| FR-2.1.1 | Users can register with email and password via Better Auth | Must Have |
| FR-2.1.2 | Users can login with email and password via Better Auth | Must Have |
| FR-2.1.3 | Users can logout (session invalidation) | Must Have |
| FR-2.1.4 | Passwords securely hashed by Better Auth | Must Have |

### 2.2 Task Management (Authenticated)
| ID | Requirement | Priority |
|----|-------------|----------|
| FR-2.2.1 | Users can create tasks with title and description | Must Have |
| FR-2.2.2 | Users can view their own tasks only | Must Have |
| FR-2.2.3 | Users can update their own tasks | Must Have |
| FR-2.2.4 | Users can delete their own tasks | Must Have |
| FR-2.2.5 | Users can mark tasks as complete/incomplete | Must Have |

### 2.3 Data Isolation
| ID | Requirement | Priority |
|----|-------------|----------|
| FR-2.3.1 | Users cannot view other users' tasks | Must Have |
| FR-2.3.2 | Users cannot modify other users' tasks | Must Have |
| FR-2.3.3 | All task queries must filter by authenticated user | Must Have |

---

## 3. Non-Functional Requirements

### 3.1 Security
| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-3.1.1 | JWT tokens validated via JWKS endpoint | Must Have |
| NFR-3.1.2 | Passwords hashed by Better Auth (Argon2/bcrypt) | Must Have |
| NFR-3.1.3 | HTTPS required in production | Must Have |
| NFR-3.1.4 | SQL injection prevention via SQLModel ORM | Must Have |
| NFR-3.1.5 | XSS prevention in frontend | Must Have |

### 3.2 Performance
| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-3.2.1 | API response time < 500ms for CRUD operations | Should Have |
| NFR-3.2.2 | Support concurrent users (Neon serverless scaling) | Should Have |

### 3.3 Reliability
| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-3.3.1 | Database persistence with Neon PostgreSQL | Must Have |
| NFR-3.3.2 | Graceful error handling with user-friendly messages | Must Have |

---

## 4. Technical Stack

### 4.1 Backend (FastAPI)
| Component | Technology |
|-----------|------------|
| Runtime | Python 3.13+ |
| Framework | FastAPI |
| Database | Neon Serverless PostgreSQL |
| ORM | SQLModel |
| JWT Validation | PyJWT + JWKS from Better Auth |
| Package Manager | UV |

### 4.2 Frontend (Next.js + Better Auth)
| Component | Technology |
|-----------|------------|
| Framework | Next.js 14+ (App Router) |
| Language | TypeScript |
| Styling | Tailwind CSS |
| Authentication | Better Auth + JWT plugin |
| State Management | React Context + useState |
| HTTP Client | fetch API with JWT headers |
| Package Manager | pnpm |

### 4.3 Infrastructure
| Component | Technology |
|---------|------------|
| Database | Neon Serverless PostgreSQL |
| Auth Server | Next.js (Better Auth handler) |
| Backend Hosting | TBD (Vercel/Railway/Fly.io) |
| Frontend Hosting | Vercel |

---

## 5. Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                       Frontend (Next.js)                     │
│  ┌─────────────────┐    ┌─────────────────────────────────┐ │
│  │   Better Auth   │    │         Task UI                 │ │
│  │   (/api/auth)   │    │  (Protected Routes)             │ │
│  │   - Login       │    │  - List Tasks                   │ │
│  │   - Register    │    │  - Create/Edit/Delete           │ │
│  │   - JWT Token   │    │  - Toggle Complete              │ │
│  │   - JWKS        │    │                                 │ │
│  └────────┬────────┘    └─────────────┬───────────────────┘ │
│           │                           │                      │
│           │ Session                   │ JWT in Header        │
│           ▼                           ▼                      │
└───────────────────────────────────────────────────────────────┘
                           │
                           │ HTTPS + JWT
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    Backend (FastAPI)                         │
│  ┌─────────────────────────────────────────────────────────┐│
│  │  JWT Middleware                                          ││
│  │  - Fetch JWKS from Next.js                              ││
│  │  - Validate JWT signature                               ││
│  │  - Extract user_id                                      ││
│  └─────────────────────────────────────────────────────────┘│
│  ┌─────────────────────────────────────────────────────────┐│
│  │  Task API (/api/v1/tasks)                               ││
│  │  - GET    /tasks          (list user's tasks)           ││
│  │  - POST   /tasks          (create task)                 ││
│  │  - GET    /tasks/{id}     (get task)                    ││
│  │  - PATCH  /tasks/{id}     (update task)                 ││
│  │  - DELETE /tasks/{id}     (delete task)                 ││
│  │  - POST   /tasks/{id}/toggle (toggle complete)          ││
│  └─────────────────────────────────────────────────────────┘│
└───────────────────────────────────────────────────────────────┘
                           │
                           │ SQLModel
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              Neon Serverless PostgreSQL                      │
│  ┌─────────────────┐    ┌─────────────────────────────────┐ │
│  │      users      │    │            tasks                │ │
│  │  (Better Auth)  │◄───│  user_id (FK)                   │ │
│  └─────────────────┘    └─────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## 6. Project Structure

```
todo-app/
├── specs/
│   ├── phase1/                 # Phase I specs (reference)
│   └── phase2/                 # Phase II specs (READ FIRST)
│       ├── requirements.md
│       ├── data-model.md
│       ├── api-spec.md
│       ├── auth-spec.md
│       ├── database-spec.md
│       ├── frontend-spec.md
│       └── acceptance-criteria.md
├── backend/                    # FastAPI backend (Task API only)
│   ├── src/todo_api/
│   │   ├── __init__.py
│   │   ├── main.py             # FastAPI app
│   │   ├── config.py           # Settings
│   │   ├── database.py         # SQLModel setup
│   │   ├── models.py           # SQLModel models
│   │   ├── schemas.py          # Pydantic schemas
│   │   ├── routers/
│   │   │   └── tasks.py        # Task CRUD routes
│   │   └── auth/
│   │       └── jwt.py          # JWKS validation
│   ├── tests/
│   ├── pyproject.toml
│   └── .env.example
├── frontend/                   # Next.js frontend + Better Auth
│   ├── src/
│   │   ├── app/
│   │   │   ├── api/auth/[...all]/  # Better Auth handler
│   │   │   ├── login/
│   │   │   ├── register/
│   │   │   └── tasks/
│   │   ├── components/
│   │   ├── lib/
│   │   │   ├── auth.ts         # Better Auth config
│   │   │   ├── auth-client.ts  # Better Auth client
│   │   │   └── api.ts          # Task API client
│   │   └── types/
│   ├── package.json
│   └── .env.example
├── src/todo/                   # Phase I (preserved)
├── CLAUDE.md
├── constitution.md
└── README.md
```

---

## 7. Scope Boundaries

### 7.1 In Scope
- User registration and authentication via Better Auth
- JWT token issuance and validation
- CRUD operations for tasks
- PostgreSQL persistence via SQLModel
- RESTful API for tasks
- Responsive web UI

### 7.2 Out of Scope
- AI chatbot features (Phase III)
- Email verification
- Password reset
- Notifications and reminders
- Role-based permissions
- Task sharing between users
- Task categories/tags
- Due dates and priorities
- Social login (Google, GitHub, etc.)

---

## 8. Success Criteria

1. **Authentication Works**
   - Users can register, login, and logout via Better Auth
   - JWT tokens are properly issued
   - Backend validates JWTs via JWKS

2. **Data Isolation Enforced**
   - Users only see their own tasks
   - API rejects cross-user access attempts

3. **Full CRUD Functionality**
   - All task operations work via web UI
   - Data persists across sessions

4. **Security Requirements Met**
   - Passwords are never stored in plaintext
   - SQL injection is prevented
   - XSS is prevented

---

## 9. Dependencies

### 9.1 External Services
| Service | Purpose | Account Required |
|---------|---------|------------------|
| Neon | PostgreSQL database | Yes (free tier) |
| Vercel | Frontend + Backend hosting | Yes (free tier) |

### 9.2 Key Libraries
| Library | Purpose | Package |
|---------|---------|---------|
| Better Auth | Authentication | `better-auth` |
| SQLModel | ORM | `sqlmodel` |
| FastAPI | Backend framework | `fastapi` |
| PyJWT | JWT validation | `pyjwt` |
| Next.js | Frontend framework | `next` |
