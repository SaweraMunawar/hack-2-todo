# Phase II Data Model Specification

## Document Information
- **Phase**: II - Todo Full-Stack Web Application
- **Version**: 2.0.0

---

## 1. Entity Overview

Phase II uses two separate data stores:
1. **Better Auth tables** - User, Session, Account, JWKS (managed by Better Auth)
2. **Task table** - Application data (managed by SQLModel)

The `user_id` in tasks references the Better Auth user ID.

---

## 2. User Entity (Better Auth)

Better Auth manages user data. The backend only needs the user ID from JWT.

### 2.1 Better Auth User Schema

```sql
CREATE TABLE "user" (
    id TEXT PRIMARY KEY,           -- UUID as string
    name TEXT,                      -- Display name
    email TEXT UNIQUE NOT NULL,     -- Email address
    emailVerified BOOLEAN,          -- Email verification status
    image TEXT,                     -- Profile image URL
    createdAt TIMESTAMP,            -- Account creation
    updatedAt TIMESTAMP             -- Last update
);
```

### 2.2 User ID in JWT

The user ID is available in the JWT `sub` claim:

```json
{
  "sub": "cm5abc123xyz...",
  "email": "user@example.com",
  "iat": 1705312200,
  "exp": 1705398600
}
```

---

## 3. Task Entity (SQLModel)

### 3.1 SQLModel Definition

```python
# models.py
from datetime import datetime, timezone
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field
from typing import Optional

class TaskBase(SQLModel):
    """Shared task fields for create/update operations."""
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=1000)


class Task(TaskBase, table=True):
    """Task database model."""
    __tablename__ = "tasks"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: str = Field(index=True, nullable=False)  # Better Auth user ID (TEXT)
    completed: bool = Field(default=False)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: Optional[datetime] = Field(default=None)


class TaskCreate(TaskBase):
    """Schema for creating a task."""
    pass


class TaskUpdate(SQLModel):
    """Schema for updating a task (all fields optional)."""
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: Optional[bool] = None


class TaskRead(TaskBase):
    """Schema for reading a task."""
    id: UUID
    completed: bool
    created_at: datetime
    updated_at: Optional[datetime]
```

### 3.2 Field Specifications

| Field | Type | Constraints | Default |
|-------|------|-------------|---------|
| `id` | `UUID` | Primary key, auto-generated | `uuid4()` |
| `user_id` | `str` | NOT NULL, indexed, references Better Auth user | Required |
| `title` | `str` | 1-200 characters, non-empty | Required |
| `description` | `str` | 0-1000 characters | `""` |
| `completed` | `bool` | `True` or `False` | `False` |
| `created_at` | `datetime` | UTC timestamp | Current time |
| `updated_at` | `datetime?` | UTC timestamp | `None` |

### 3.3 Validation Rules

#### Title Validation
- Must not be empty after stripping whitespace
- Length: 1-200 characters
- Leading/trailing whitespace is trimmed

```python
from pydantic import field_validator

class TaskCreate(TaskBase):
    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Title cannot be empty")
        if len(v) > 200:
            raise ValueError("Title must be 200 characters or less")
        return v
```

#### Description Validation
- Optional (empty string allowed)
- Maximum 1000 characters
- Leading/trailing whitespace is trimmed

```python
@field_validator("description")
@classmethod
def validate_description(cls, v: str) -> str:
    v = v.strip()
    if len(v) > 1000:
        raise ValueError("Description must be 1000 characters or less")
    return v
```

---

## 4. Entity Relationships

```
┌──────────────────────────────────┐
│    Better Auth "user" table      │
├──────────────────────────────────┤
│ id (PK)        TEXT              │
│ email          TEXT UNIQUE       │
│ name           TEXT              │
│ ...                              │
└──────────────────────────────────┘
                │
                │ 1
                │ (referenced by user_id)
                ▼ N
┌──────────────────────────────────┐
│         tasks (SQLModel)         │
├──────────────────────────────────┤
│ id             UUID       PK     │
│ user_id        TEXT       INDEX  │
│ title          VARCHAR(200)      │
│ description    TEXT              │
│ completed      BOOLEAN           │
│ created_at     TIMESTAMPTZ       │
│ updated_at     TIMESTAMPTZ       │
└──────────────────────────────────┘
```

**Note:** No foreign key constraint between tasks and Better Auth users because:
- Better Auth tables are managed separately
- User ID comes from validated JWT (already authenticated)
- Simplifies deployment and testing

---

## 5. API Schemas

### 5.1 Request Schemas

```python
# TaskCreate - POST /tasks
class TaskCreate(SQLModel):
    title: str
    description: str = ""

# Example request body
{
    "title": "Buy groceries",
    "description": "Get milk, eggs, bread"
}
```

```python
# TaskUpdate - PATCH /tasks/{id}
class TaskUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None

# Example request body (partial update)
{
    "completed": true
}
```

### 5.2 Response Schemas

```python
# TaskRead - Single task response
class TaskRead(SQLModel):
    id: UUID
    title: str
    description: str
    completed: bool
    created_at: datetime
    updated_at: Optional[datetime]

# Example response
{
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "title": "Buy groceries",
    "description": "Get milk, eggs, bread",
    "completed": false,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": null
}
```

```python
# TaskListResponse - List tasks response
class TaskListResponse(SQLModel):
    tasks: list[TaskRead]
    total: int

# Example response
{
    "tasks": [...],
    "total": 5
}
```

---

## 6. TypeScript Types (Frontend)

```typescript
// types/index.ts

// Task types
export interface Task {
  id: string;
  title: string;
  description: string;
  completed: boolean;
  created_at: string;  // ISO 8601
  updated_at: string | null;
}

export interface TaskCreate {
  title: string;
  description?: string;
}

export interface TaskUpdate {
  title?: string;
  description?: string;
  completed?: boolean;
}

export interface TaskListResponse {
  tasks: Task[];
  total: number;
}

// User from Better Auth session
export interface User {
  id: string;
  name: string | null;
  email: string;
  emailVerified: boolean;
  image: string | null;
  createdAt: Date;
  updatedAt: Date;
}

export interface Session {
  user: User;
  session: {
    id: string;
    userId: string;
    token: string;
    expiresAt: Date;
  };
}
```

---

## 7. Data Access Patterns

### 7.1 Task Operations (SQLModel)

All task operations are scoped to the authenticated user.

```python
from sqlmodel import Session, select
from uuid import UUID

# List user's tasks
def get_user_tasks(
    db: Session,
    user_id: str,
    completed: bool | None = None,
    limit: int = 50,
    offset: int = 0
) -> list[Task]:
    statement = select(Task).where(Task.user_id == user_id)

    if completed is not None:
        statement = statement.where(Task.completed == completed)

    statement = statement.order_by(Task.created_at.desc())
    statement = statement.offset(offset).limit(limit)

    return db.exec(statement).all()


# Get single task (with ownership check)
def get_task(db: Session, task_id: UUID, user_id: str) -> Task | None:
    statement = select(Task).where(
        Task.id == task_id,
        Task.user_id == user_id
    )
    return db.exec(statement).first()


# Create task
def create_task(db: Session, user_id: str, data: TaskCreate) -> Task:
    task = Task(
        user_id=user_id,
        title=data.title,
        description=data.description,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


# Update task
def update_task(db: Session, task: Task, data: TaskUpdate) -> Task:
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)
    task.updated_at = datetime.now(timezone.utc)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


# Delete task
def delete_task(db: Session, task: Task) -> None:
    db.delete(task)
    db.commit()


# Toggle completion
def toggle_task(db: Session, task: Task) -> Task:
    task.completed = not task.completed
    task.updated_at = datetime.now(timezone.utc)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task
```

**CRITICAL:** Every task query MUST include `user_id` filter to enforce data isolation.

---

## 8. Error Messages

| Scenario | HTTP Status | Message |
|----------|-------------|---------|
| Empty title | 422 | "Title cannot be empty" |
| Title too long | 422 | "Title must be 200 characters or less" |
| Description too long | 422 | "Description must be 1000 characters or less" |
| Task not found | 404 | "Task not found" |
| Not authenticated | 401 | "Not authenticated" |
| Invalid token | 401 | "Invalid authentication token" |

---

## 9. Database Index Strategy

```sql
-- Primary index on task ID (automatic)
-- User ID index for listing tasks
CREATE INDEX idx_tasks_user_id ON tasks(user_id);

-- Optional: Composite index for filtered queries
CREATE INDEX idx_tasks_user_completed ON tasks(user_id, completed);

-- Optional: Index for sorting by created_at
CREATE INDEX idx_tasks_user_created ON tasks(user_id, created_at DESC);
```

SQLModel creates the `user_id` index automatically via `Field(index=True)`.
