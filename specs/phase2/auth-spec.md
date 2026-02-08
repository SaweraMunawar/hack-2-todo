# Phase II Authentication Specification

## Document Information
- **Phase**: II - Todo Full-Stack Web Application
- **Version**: 2.1.0

---

## 1. Overview

Authentication is handled by **Better Auth** running in the Next.js frontend. The FastAPI backend validates JWT tokens using a **shared secret** (symmetric HS256).

### 1.1 Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    Next.js Frontend                           │
│  ┌────────────────────────────────────────────────────────┐  │
│  │                    Better Auth                          │  │
│  │  ┌──────────────┐  ┌──────────────┐                    │  │
│  │  │ /api/auth/*  │  │ /api/auth/   │                    │  │
│  │  │  Handler     │  │   token      │                    │  │
│  │  │              │  │  (JWT)       │                    │  │
│  │  │ - signup     │  │              │                    │  │
│  │  │ - signin     │  │              │                    │  │
│  │  │ - signout    │  │              │                    │  │
│  │  │ - session    │  │              │                    │  │
│  │  └──────────────┘  └──────────────┘                    │  │
│  └────────────────────────────────────────────────────────┘  │
│                              │                                │
│                              │ Neon PostgreSQL                │
│                              ▼                                │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  Database Tables (managed by Better Auth)              │  │
│  │  - users                                               │  │
│  │  - sessions                                            │  │
│  │  - accounts                                            │  │
│  │  - verifications                                       │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
                              │
                              │ JWT Token (HS256)
                              ▼
┌──────────────────────────────────────────────────────────────┐
│                    FastAPI Backend                            │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  JWT Validation Middleware                              │  │
│  │  1. Extract JWT from Authorization header              │  │
│  │  2. Verify signature using BETTER_AUTH_SECRET          │  │
│  │  3. Validate claims (exp)                              │  │
│  │  4. Extract user_id from payload                       │  │
│  │  5. Pass user_id to route handlers                     │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

### 1.2 Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| JWT Algorithm | HS256 (symmetric) | Simpler setup, shared secret |
| Token Validation | Shared secret | No JWKS endpoint needed |
| Session Management | Better Auth only | FastAPI is stateless |

---

## 2. Better Auth Configuration

### 2.1 Installation

```bash
# In frontend directory
pnpm add better-auth
```

### 2.2 Server Configuration

```typescript
// lib/auth.ts
import { betterAuth } from "better-auth";
import { jwt } from "better-auth/plugins";
import { Pool } from "pg";

export const auth = betterAuth({
  database: new Pool({
    connectionString: process.env.DATABASE_URL,
  }),

  emailAndPassword: {
    enabled: true,
    requireEmailVerification: false, // Out of scope for Phase II
  },

  plugins: [
    jwt({
      jwt: {
        expirationTime: "1h", // Token expires in 1 hour
      },
    }),
  ],
});

export type Session = typeof auth.$Infer.Session;
```

### 2.3 API Route Handler

```typescript
// app/api/auth/[...all]/route.ts
import { auth } from "@/lib/auth";
import { toNextJsHandler } from "better-auth/next-js";

export const { GET, POST } = toNextJsHandler(auth);
```

### 2.4 Client Configuration

```typescript
// lib/auth-client.ts
import { createAuthClient } from "better-auth/react";
import { jwtClient } from "better-auth/client/plugins";

export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_APP_URL,
  plugins: [jwtClient()],
});

export const {
  signIn,
  signUp,
  signOut,
  useSession,
  getSession,
} = authClient;
```

---

## 3. JWT Token Specification

### 3.1 Token Structure

Better Auth JWT plugin generates standard JWT tokens signed with HS256.

**Header:**
```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

**Payload:**
```json
{
  "sub": "user-id",
  "email": "user@example.com",
  "iat": 1705312200,
  "exp": 1705315800
}
```

### 3.2 Token Retrieval

```typescript
// Get JWT token for API calls
const { token } = await authClient.token();

// Use token in API request
fetch('https://api.example.com/api/v1/tasks', {
  headers: {
    Authorization: `Bearer ${token}`,
  },
});
```

---

## 4. FastAPI JWT Validation

### 4.1 Dependencies

```toml
# pyproject.toml
[project]
dependencies = [
    "fastapi>=0.115.0",
    "pyjwt>=2.8.0",
]
```

### 4.2 JWT Verification with Shared Secret

```python
# auth/jwt.py
import jwt
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from ..config import settings

security = HTTPBearer()


def decode_jwt(token: str) -> dict:
    """
    Decode and validate JWT using shared secret.

    Steps:
    1. Verify signature using BETTER_AUTH_SECRET
    2. Validate claims (exp)
    3. Return payload

    Raises:
        HTTPException(401): If token is invalid
    """
    try:
        payload = jwt.decode(
            token,
            settings.BETTER_AUTH_SECRET,
            algorithms=["HS256"],
        )
        return payload

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid authentication token")
```

### 4.3 Authentication Dependency

```python
# auth/jwt.py (continued)
from dataclasses import dataclass


@dataclass
class CurrentUser:
    """Authenticated user from JWT."""
    id: str
    email: str


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> CurrentUser:
    """
    FastAPI dependency to extract and validate JWT.

    Usage:
        @app.get("/tasks")
        async def list_tasks(user: CurrentUser = Depends(get_current_user)):
            ...
    """
    token = credentials.credentials
    payload = decode_jwt(token)

    return CurrentUser(
        id=payload["sub"],
        email=payload.get("email", ""),
    )
```

### 4.4 Configuration

```python
# config.py
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    BETTER_AUTH_SECRET: str  # Shared secret for JWT verification

    class Config:
        env_file = ".env"


settings = Settings()
```

---

## 5. Authentication Flows

### 5.1 Registration Flow

```
Browser                    Next.js                    Better Auth DB
   │                          │                              │
   │  signUp(email, pass)     │                              │
   │─────────────────────────►│                              │
   │                          │                              │
   │                          │  Hash password               │
   │                          │  Create user                 │
   │                          │─────────────────────────────►│
   │                          │                              │
   │                          │  Create session              │
   │                          │─────────────────────────────►│
   │                          │                              │
   │  session cookie set      │                              │
   │◄─────────────────────────│                              │
   │                          │                              │
```

### 5.2 Login Flow

```
Browser                    Next.js                    Better Auth DB
   │                          │                              │
   │  signIn(email, pass)     │                              │
   │─────────────────────────►│                              │
   │                          │                              │
   │                          │  Find user by email          │
   │                          │─────────────────────────────►│
   │                          │                              │
   │                          │  Verify password             │
   │                          │                              │
   │                          │  Create session              │
   │                          │─────────────────────────────►│
   │                          │                              │
   │  session cookie set      │                              │
   │◄─────────────────────────│                              │
   │                          │                              │
```

### 5.3 API Request Flow (JWT)

```
Browser                Next.js              FastAPI             Task DB
   │                      │                    │                   │
   │  authClient.token()  │                    │                   │
   │─────────────────────►│                    │                   │
   │                      │                    │                   │
   │  JWT token (HS256)   │                    │                   │
   │◄─────────────────────│                    │                   │
   │                      │                    │                   │
   │  GET /api/v1/tasks                        │                   │
   │  Authorization: Bearer <token>            │                   │
   │──────────────────────────────────────────►│                   │
   │                      │                    │                   │
   │                      │                    │  Verify JWT       │
   │                      │                    │  (shared secret)  │
   │                      │                    │                   │
   │                      │                    │  Extract user_id  │
   │                      │                    │                   │
   │                      │                    │  SELECT tasks     │
   │                      │                    │  WHERE user_id=X  │
   │                      │                    │──────────────────►│
   │                      │                    │                   │
   │                      │                    │  tasks            │
   │                      │                    │◄──────────────────│
   │                      │                    │                   │
   │  200 OK { tasks }    │                    │                   │
   │◄──────────────────────────────────────────│                   │
   │                      │                    │                   │
```

---

## 6. Environment Variables

### 6.1 Frontend (.env)

```bash
# Database for Better Auth
DATABASE_URL=postgresql://user:password@host/dbname?sslmode=require

# Better Auth secret (min 32 chars) - SHARED WITH BACKEND
BETTER_AUTH_SECRET=your-32-character-secret-key-here

# App URL
NEXT_PUBLIC_APP_URL=http://localhost:3000

# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

### 6.2 Backend (.env)

```bash
# Database for tasks
DATABASE_URL=postgresql://user:password@host/dbname?sslmode=require

# Better Auth secret - SAME AS FRONTEND
BETTER_AUTH_SECRET=your-32-character-secret-key-here
```

**CRITICAL:** Both frontend and backend must use the same `BETTER_AUTH_SECRET` value.

---

## 7. Security Considerations

### 7.1 Implemented

| Measure | Description |
|---------|-------------|
| Password hashing | Handled by Better Auth (Argon2/bcrypt) |
| JWT signing | HS256 with shared secret |
| Token expiration | 1 hour default |
| Secure cookies | HttpOnly, Secure, SameSite |
| User isolation | All queries filtered by user_id from JWT |

### 7.2 Security Rules

| Rule | Implementation |
|------|----------------|
| Missing token | 401 Unauthorized |
| Invalid token | 401 Unauthorized |
| Expired token | 401 "Token has expired" |
| Wrong user's resource | 404 Not Found (not 403) |

### 7.3 Error Handling

| Condition | HTTP Status | Message |
|-----------|-------------|---------|
| Missing Authorization header | 401 | "Not authenticated" |
| Invalid token format | 401 | "Invalid authentication token" |
| Expired token | 401 | "Token has expired" |
| Invalid signature | 401 | "Invalid authentication token" |

---

## 8. Database Schema (Better Auth)

Better Auth automatically creates these tables:

```sql
-- users table
CREATE TABLE "user" (
    id TEXT PRIMARY KEY,
    name TEXT,
    email TEXT UNIQUE NOT NULL,
    emailVerified BOOLEAN,
    image TEXT,
    createdAt TIMESTAMP,
    updatedAt TIMESTAMP
);

-- sessions table
CREATE TABLE "session" (
    id TEXT PRIMARY KEY,
    userId TEXT NOT NULL REFERENCES "user"(id),
    token TEXT UNIQUE NOT NULL,
    expiresAt TIMESTAMP NOT NULL,
    ipAddress TEXT,
    userAgent TEXT,
    createdAt TIMESTAMP,
    updatedAt TIMESTAMP
);

-- accounts table (for OAuth, not used in Phase II)
CREATE TABLE "account" (
    id TEXT PRIMARY KEY,
    userId TEXT NOT NULL REFERENCES "user"(id),
    accountId TEXT NOT NULL,
    providerId TEXT NOT NULL,
    accessToken TEXT,
    refreshToken TEXT,
    accessTokenExpiresAt TIMESTAMP,
    refreshTokenExpiresAt TIMESTAMP,
    scope TEXT,
    idToken TEXT,
    password TEXT,
    createdAt TIMESTAMP,
    updatedAt TIMESTAMP
);
```

**Note:** Use Better Auth CLI to generate/migrate schema:
```bash
npx @better-auth/cli generate
npx @better-auth/cli migrate
```

---

## 9. Frontend Auth Components

### 9.1 useSession Hook

```typescript
"use client";

import { useSession } from "@/lib/auth-client";

export function UserProfile() {
  const { data: session, isPending } = useSession();

  if (isPending) return <div>Loading...</div>;
  if (!session) return <div>Not logged in</div>;

  return (
    <div>
      <p>Email: {session.user.email}</p>
      <button onClick={() => signOut()}>Logout</button>
    </div>
  );
}
```

### 9.2 Protected Route Pattern

```typescript
// app/tasks/page.tsx
import { auth } from "@/lib/auth";
import { headers } from "next/headers";
import { redirect } from "next/navigation";

export default async function TasksPage() {
  const session = await auth.api.getSession({
    headers: await headers(),
  });

  if (!session) {
    redirect("/login");
  }

  // Render protected content
  return <TaskList />;
}
```

### 9.3 API Client with Token

```typescript
// lib/api.ts
import { authClient } from "./auth-client";

const API_URL = process.env.NEXT_PUBLIC_API_URL;

export async function fetchWithAuth(
  endpoint: string,
  options: RequestInit = {}
): Promise<Response> {
  // Get JWT token from Better Auth
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
    // Token expired or invalid, redirect to login
    window.location.href = "/login";
    throw new Error("Session expired");
  }

  return response;
}
```
