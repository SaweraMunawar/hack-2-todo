# Phase II API Specification

## Document Information
- **Phase**: II - Todo Full-Stack Web Application
- **Version**: 2.0.0
- **Base URL**: `/api/v1`

---

## 1. Overview

### 1.1 API Architecture

The application uses **two separate APIs**:

1. **Better Auth API** (Next.js) - Handles authentication
   - Base: `/api/auth`
   - Managed by Better Auth

2. **Task API** (FastAPI) - Handles task CRUD
   - Base: `/api/v1`
   - JWT-secured via Better Auth JWKS

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend                              │
│                                                              │
│  ┌──────────────────────┐    ┌──────────────────────────┐   │
│  │   Auth Operations    │    │     Task Operations      │   │
│  │                      │    │                          │   │
│  │  authClient.signUp() │    │  fetchWithAuth('/tasks') │   │
│  │  authClient.signIn() │    │                          │   │
│  │  authClient.signOut()│    │                          │   │
│  │  authClient.token()  │    │                          │   │
│  └──────────┬───────────┘    └────────────┬─────────────┘   │
│             │                              │                 │
└─────────────│──────────────────────────────│─────────────────┘
              │                              │
              ▼                              ▼
┌─────────────────────────┐    ┌─────────────────────────────┐
│    Next.js /api/auth    │    │    FastAPI /api/v1/tasks    │
│    (Better Auth)        │    │    (Task CRUD)              │
│                         │    │                             │
│  POST /sign-up/email    │    │  GET    /tasks              │
│  POST /sign-in/email    │    │  POST   /tasks              │
│  POST /sign-out         │    │  GET    /tasks/{id}         │
│  GET  /get-session      │    │  PATCH  /tasks/{id}         │
│  POST /token            │    │  DELETE /tasks/{id}         │
│  GET  /jwks             │    │  POST   /tasks/{id}/toggle  │
└─────────────────────────┘    │  GET    /health             │
                               └─────────────────────────────┘
```

### 1.2 Response Format

**Success Response:**
```json
{
  "id": "...",
  "title": "...",
  ...
}
```

**Error Response:**
```json
{
  "detail": "Error message"
}
```

**Validation Error Response (422):**
```json
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "Title cannot be empty",
      "type": "value_error"
    }
  ]
}
```

---

## 2. Better Auth Endpoints (Next.js)

Better Auth provides these endpoints automatically at `/api/auth/*`.

### 2.1 Sign Up

**Endpoint:** `POST /api/auth/sign-up/email`

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123",
  "name": "John Doe"
}
```

**Success Response (200 OK):**
```json
{
  "user": {
    "id": "cm5abc123xyz...",
    "email": "user@example.com",
    "name": "John Doe",
    "emailVerified": false,
    "createdAt": "2024-01-15T10:30:00Z",
    "updatedAt": "2024-01-15T10:30:00Z"
  },
  "session": {
    "id": "session-id",
    "userId": "cm5abc123xyz...",
    "token": "session-token",
    "expiresAt": "2024-01-22T10:30:00Z"
  }
}
```

**Note:** Use Better Auth client `authClient.signUp.email()` instead of direct fetch.

### 2.2 Sign In

**Endpoint:** `POST /api/auth/sign-in/email`

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123"
}
```

**Success Response (200 OK):**
```json
{
  "user": { ... },
  "session": { ... }
}
```

### 2.3 Sign Out

**Endpoint:** `POST /api/auth/sign-out`

**Headers:**
```
Cookie: better-auth.session_token=...
```

**Success Response (200 OK):**
```json
{
  "success": true
}
```

### 2.4 Get Session

**Endpoint:** `GET /api/auth/get-session`

**Headers:**
```
Cookie: better-auth.session_token=...
```

**Success Response (200 OK):**
```json
{
  "user": { ... },
  "session": { ... }
}
```

### 2.5 Get JWT Token

**Endpoint:** `POST /api/auth/token`

**Headers:**
```
Cookie: better-auth.session_token=...
```

**Success Response (200 OK):**
```json
{
  "token": "eyJhbGciOiJSUzI1NiIs..."
}
```

### 2.6 JWKS Endpoint

**Endpoint:** `GET /api/auth/jwks`

**Success Response (200 OK):**
```json
{
  "keys": [
    {
      "kty": "RSA",
      "kid": "key-id",
      "use": "sig",
      "alg": "RS256",
      "n": "...",
      "e": "AQAB"
    }
  ]
}
```

---

## 3. Task API Endpoints (FastAPI)

All task endpoints require JWT authentication.

### 3.1 List Tasks

**Endpoint:** `GET /api/v1/tasks`

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `completed` | bool | - | Filter by completion status |
| `limit` | int | 50 | Max tasks to return (1-100) |
| `offset` | int | 0 | Pagination offset |

**Success Response (200 OK):**
```json
{
  "tasks": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440001",
      "title": "Buy groceries",
      "description": "Get milk, eggs, bread",
      "completed": false,
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": null
    }
  ],
  "total": 1
}
```

**Notes:**
- Tasks are ordered by `created_at DESC` (newest first)
- Only returns tasks belonging to authenticated user

---

### 3.2 Create Task

**Endpoint:** `POST /api/v1/tasks`

**Headers:**
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request:**
```json
{
  "title": "Buy groceries",
  "description": "Get milk, eggs, bread"
}
```

**Success Response (201 Created):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "title": "Buy groceries",
  "description": "Get milk, eggs, bread",
  "completed": false,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": null
}
```

**Error Responses:**

| Status | Condition | Response |
|--------|-----------|----------|
| 401 | Not authenticated | `{"detail": "Not authenticated"}` |
| 422 | Empty title | `{"detail": [{"loc": ["body", "title"], "msg": "Title cannot be empty"}]}` |
| 422 | Title too long | `{"detail": [{"loc": ["body", "title"], "msg": "String should have at most 200 characters"}]}` |

---

### 3.3 Get Task

**Endpoint:** `GET /api/v1/tasks/{task_id}`

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `task_id` | UUID | Task identifier |

**Success Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "title": "Buy groceries",
  "description": "Get milk, eggs, bread",
  "completed": false,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": null
}
```

**Error Responses:**

| Status | Condition | Response |
|--------|-----------|----------|
| 401 | Not authenticated | `{"detail": "Not authenticated"}` |
| 404 | Task not found | `{"detail": "Task not found"}` |
| 404 | Task belongs to another user | `{"detail": "Task not found"}` |

**Security Note:** Returns 404 (not 403) for tasks belonging to other users to prevent enumeration attacks.

---

### 3.4 Update Task

**Endpoint:** `PATCH /api/v1/tasks/{task_id}`

**Headers:**
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `task_id` | UUID | Task identifier |

**Request (Partial Update):**
```json
{
  "title": "Buy groceries today",
  "completed": true
}
```

All fields are optional. Only provided fields are updated.

**Success Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "title": "Buy groceries today",
  "description": "Get milk, eggs, bread",
  "completed": true,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T14:00:00Z"
}
```

**Error Responses:**

| Status | Condition | Response |
|--------|-----------|----------|
| 401 | Not authenticated | `{"detail": "Not authenticated"}` |
| 404 | Task not found | `{"detail": "Task not found"}` |
| 422 | Invalid field value | `{"detail": [...]}` |

---

### 3.5 Delete Task

**Endpoint:** `DELETE /api/v1/tasks/{task_id}`

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `task_id` | UUID | Task identifier |

**Success Response (204 No Content):**
```
(empty body)
```

**Error Responses:**

| Status | Condition | Response |
|--------|-----------|----------|
| 401 | Not authenticated | `{"detail": "Not authenticated"}` |
| 404 | Task not found | `{"detail": "Task not found"}` |

---

### 3.6 Toggle Task Completion

**Endpoint:** `POST /api/v1/tasks/{task_id}/toggle`

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `task_id` | UUID | Task identifier |

**Success Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "title": "Buy groceries",
  "description": "Get milk, eggs, bread",
  "completed": true,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T14:00:00Z"
}
```

**Error Responses:**

| Status | Condition | Response |
|--------|-----------|----------|
| 401 | Not authenticated | `{"detail": "Not authenticated"}` |
| 404 | Task not found | `{"detail": "Task not found"}` |

---

## 4. Health Check

### 4.1 API Health

**Endpoint:** `GET /api/v1/health`

**Success Response (200 OK):**
```json
{
  "status": "healthy",
  "database": "connected",
  "version": "1.0.0"
}
```

---

## 5. OpenAPI Documentation

FastAPI automatically generates OpenAPI documentation:

| Endpoint | Description |
|----------|-------------|
| `/docs` | Swagger UI |
| `/redoc` | ReDoc UI |
| `/openapi.json` | OpenAPI schema |

---

## 6. Frontend API Client

### 6.1 Auth Client (Better Auth)

```typescript
// lib/auth-client.ts
import { createAuthClient } from "better-auth/react";
import { jwtClient } from "better-auth/client/plugins";

export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_APP_URL,
  plugins: [jwtClient()],
});

// Usage
await authClient.signUp.email({
  email: "user@example.com",
  password: "SecurePass123",
  name: "John Doe",
});

await authClient.signIn.email({
  email: "user@example.com",
  password: "SecurePass123",
});

await authClient.signOut();

const { token } = await authClient.token();
```

### 6.2 Task API Client

```typescript
// lib/api.ts
import { authClient } from "./auth-client";

const API_URL = process.env.NEXT_PUBLIC_API_URL;

async function fetchWithAuth(
  endpoint: string,
  options: RequestInit = {}
): Promise<Response> {
  const { token } = await authClient.token();

  if (!token) {
    throw new Error("Not authenticated");
  }

  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
      ...options.headers,
    },
  });

  if (response.status === 401) {
    window.location.href = "/login";
    throw new Error("Session expired");
  }

  return response;
}

// Task API functions
export async function getTasks(params?: {
  completed?: boolean;
  limit?: number;
  offset?: number;
}): Promise<TaskListResponse> {
  const searchParams = new URLSearchParams();
  if (params?.completed !== undefined) {
    searchParams.set("completed", String(params.completed));
  }
  if (params?.limit) searchParams.set("limit", String(params.limit));
  if (params?.offset) searchParams.set("offset", String(params.offset));

  const query = searchParams.toString();
  const response = await fetchWithAuth(`/tasks${query ? `?${query}` : ""}`);
  return response.json();
}

export async function createTask(data: TaskCreate): Promise<Task> {
  const response = await fetchWithAuth("/tasks", {
    method: "POST",
    body: JSON.stringify(data),
  });
  return response.json();
}

export async function updateTask(id: string, data: TaskUpdate): Promise<Task> {
  const response = await fetchWithAuth(`/tasks/${id}`, {
    method: "PATCH",
    body: JSON.stringify(data),
  });
  return response.json();
}

export async function deleteTask(id: string): Promise<void> {
  await fetchWithAuth(`/tasks/${id}`, {
    method: "DELETE",
  });
}

export async function toggleTask(id: string): Promise<Task> {
  const response = await fetchWithAuth(`/tasks/${id}/toggle`, {
    method: "POST",
  });
  return response.json();
}
```

---

## 7. CORS Configuration

### 7.1 FastAPI CORS

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",      # Local development
        "https://your-app.vercel.app" # Production
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
```

---

## 8. Error Handling

### 8.1 HTTP Status Codes

| Status | Meaning |
|--------|---------|
| 200 | Success |
| 201 | Created |
| 204 | No Content (success, no body) |
| 400 | Bad Request |
| 401 | Unauthorized (missing/invalid auth) |
| 404 | Not Found |
| 422 | Validation Error |
| 500 | Internal Server Error |

### 8.2 Error Response Format

```json
{
  "detail": "Human-readable error message"
}
```

For validation errors:
```json
{
  "detail": [
    {
      "loc": ["body", "field_name"],
      "msg": "Error message",
      "type": "error_type"
    }
  ]
}
```
