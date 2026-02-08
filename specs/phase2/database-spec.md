# Phase II Database Specification

## Document Information
- **Phase**: II - Todo Full-Stack Web Application
- **Version**: 2.0.0
- **Database**: Neon Serverless PostgreSQL
- **ORM**: SQLModel

---

## 1. Overview

### 1.1 Database Architecture

The application uses a **shared database** with two sets of tables:
1. **Better Auth tables** - Managed by Better Auth CLI (users, sessions, accounts, jwks)
2. **Application tables** - Managed by SQLModel (tasks)

```
┌─────────────────────────────────────────────────────────────┐
│                  Neon PostgreSQL Database                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Better Auth Tables          Application Tables              │
│  ─────────────────           ──────────────────              │
│  ┌─────────────┐             ┌─────────────────┐            │
│  │    user     │◄────────────│     tasks       │            │
│  ├─────────────┤   user_id   ├─────────────────┤            │
│  │ id          │             │ id              │            │
│  │ email       │             │ user_id         │            │
│  │ name        │             │ title           │            │
│  │ ...         │             │ description     │            │
│  └─────────────┘             │ completed       │            │
│                              │ created_at      │            │
│  ┌─────────────┐             │ updated_at      │            │
│  │   session   │             └─────────────────┘            │
│  └─────────────┘                                            │
│                                                              │
│  ┌─────────────┐                                            │
│  │   account   │                                            │
│  └─────────────┘                                            │
│                                                              │
│  ┌─────────────┐                                            │
│  │    jwks     │                                            │
│  └─────────────┘                                            │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 Connection Configuration

```bash
# Shared connection string for both Better Auth and SQLModel
DATABASE_URL=postgresql://user:password@ep-xxx.region.aws.neon.tech/dbname?sslmode=require
```

---

## 2. Tasks Table Schema

### 2.1 SQL Definition

```sql
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT DEFAULT '',
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Index for user's tasks (required for performance)
CREATE INDEX idx_tasks_user_id ON tasks(user_id);

-- Optional: Composite index for filtered queries
CREATE INDEX idx_tasks_user_completed ON tasks(user_id, completed);
```

### 2.2 Column Details

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() | Unique identifier |
| user_id | TEXT | NOT NULL, INDEX | Better Auth user ID |
| title | VARCHAR(200) | NOT NULL | Task title |
| description | TEXT | DEFAULT '' | Task description |
| completed | BOOLEAN | NOT NULL, DEFAULT FALSE | Completion status |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Creation timestamp |
| updated_at | TIMESTAMPTZ | NULLABLE | Last update timestamp |

---

## 3. SQLModel Configuration

### 3.1 Engine Setup

```python
# database.py
from sqlmodel import SQLModel, Session, create_engine
from sqlalchemy.pool import NullPool

from .config import settings

# Use NullPool for serverless (Neon recommendation)
engine = create_engine(
    settings.DATABASE_URL,
    poolclass=NullPool,
    echo=False,  # Set True for SQL debugging
)


def create_db_and_tables():
    """Create all SQLModel tables."""
    SQLModel.metadata.create_all(engine)


def get_session():
    """FastAPI dependency for database sessions."""
    with Session(engine) as session:
        yield session
```

### 3.2 Task Model

```python
# models.py
from datetime import datetime, timezone
from uuid import UUID, uuid4
from typing import Optional
from sqlmodel import SQLModel, Field


class TaskBase(SQLModel):
    """Shared task fields."""
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=1000)


class Task(TaskBase, table=True):
    """Task database model."""
    __tablename__ = "tasks"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: str = Field(index=True, nullable=False)
    completed: bool = Field(default=False)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"server_default": "now()"}
    )
    updated_at: Optional[datetime] = Field(default=None)


class TaskCreate(TaskBase):
    """Schema for creating a task."""
    pass


class TaskUpdate(SQLModel):
    """Schema for updating a task."""
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: Optional[bool] = None


class TaskRead(TaskBase):
    """Schema for reading a task."""
    id: UUID
    completed: bool
    created_at: datetime
    updated_at: Optional[datetime]


class TaskListResponse(SQLModel):
    """Response schema for task list."""
    tasks: list[TaskRead]
    total: int
```

---

## 4. Database Session Management

### 4.1 FastAPI Dependency

```python
# main.py
from fastapi import FastAPI, Depends
from sqlmodel import Session
from contextlib import asynccontextmanager

from .database import create_db_and_tables, get_session
from .routers import tasks

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - create tables on startup."""
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)
app.include_router(tasks.router)
```

### 4.2 Using Sessions in Routes

```python
# routers/tasks.py
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from ..database import get_session
from ..models import Task, TaskCreate, TaskRead, TaskListResponse
from ..auth.jwt import get_current_user, CurrentUser

router = APIRouter(prefix="/api/v1/tasks", tags=["tasks"])


@router.get("", response_model=TaskListResponse)
async def list_tasks(
    user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_session),
    completed: bool | None = None,
    limit: int = 50,
    offset: int = 0,
):
    """List authenticated user's tasks."""
    statement = select(Task).where(Task.user_id == user.id)

    if completed is not None:
        statement = statement.where(Task.completed == completed)

    statement = statement.order_by(Task.created_at.desc())
    statement = statement.offset(offset).limit(limit)

    tasks = db.exec(statement).all()

    # Get total count
    count_statement = select(Task).where(Task.user_id == user.id)
    if completed is not None:
        count_statement = count_statement.where(Task.completed == completed)
    total = len(db.exec(count_statement).all())

    return TaskListResponse(tasks=tasks, total=total)
```

---

## 5. CRUD Operations

### 5.1 Create Task

```python
@router.post("", response_model=TaskRead, status_code=201)
async def create_task(
    data: TaskCreate,
    user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """Create a new task for the authenticated user."""
    task = Task(
        user_id=user.id,
        title=data.title.strip(),
        description=data.description.strip(),
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task
```

### 5.2 Get Task

```python
@router.get("/{task_id}", response_model=TaskRead)
async def get_task(
    task_id: UUID,
    user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """Get a specific task (must belong to user)."""
    statement = select(Task).where(
        Task.id == task_id,
        Task.user_id == user.id
    )
    task = db.exec(statement).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return task
```

### 5.3 Update Task

```python
@router.patch("/{task_id}", response_model=TaskRead)
async def update_task(
    task_id: UUID,
    data: TaskUpdate,
    user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """Update a task (partial update)."""
    statement = select(Task).where(
        Task.id == task_id,
        Task.user_id == user.id
    )
    task = db.exec(statement).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Apply updates
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if isinstance(value, str):
            value = value.strip()
        setattr(task, field, value)

    task.updated_at = datetime.now(timezone.utc)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task
```

### 5.4 Delete Task

```python
@router.delete("/{task_id}", status_code=204)
async def delete_task(
    task_id: UUID,
    user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """Delete a task."""
    statement = select(Task).where(
        Task.id == task_id,
        Task.user_id == user.id
    )
    task = db.exec(statement).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(task)
    db.commit()
```

### 5.5 Toggle Completion

```python
@router.post("/{task_id}/toggle", response_model=TaskRead)
async def toggle_task(
    task_id: UUID,
    user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """Toggle task completion status."""
    statement = select(Task).where(
        Task.id == task_id,
        Task.user_id == user.id
    )
    task = db.exec(statement).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.completed = not task.completed
    task.updated_at = datetime.now(timezone.utc)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task
```

---

## 6. Migrations

### 6.1 Initial Setup

SQLModel can auto-create tables, but for production use Alembic:

```bash
# Install alembic
uv add alembic

# Initialize alembic
alembic init alembic

# Configure alembic.ini with DATABASE_URL
# Edit alembic/env.py to use SQLModel metadata
```

### 6.2 Simple Migration Script

For hackathon, a simple migration script works:

```python
# migrations.py
from sqlmodel import SQLModel
from .database import engine
from .models import Task  # Import all models

def run_migrations():
    """Create all tables."""
    SQLModel.metadata.create_all(engine)

if __name__ == "__main__":
    run_migrations()
    print("Migrations complete!")
```

Run with:
```bash
uv run python -m todo_api.migrations
```

### 6.3 Raw SQL Migration

For explicit control:

```sql
-- migrations/001_create_tasks.sql

-- Enable UUID extension (Neon has this enabled by default)
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create tasks table
CREATE TABLE IF NOT EXISTS tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT DEFAULT '',
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_tasks_user_id ON tasks(user_id);
CREATE INDEX IF NOT EXISTS idx_tasks_user_completed ON tasks(user_id, completed);
```

---

## 7. Neon-Specific Configuration

### 7.1 Connection Pooling

Neon provides built-in connection pooling. Use the pooled endpoint:

```bash
# Pooled (recommended for serverless)
DATABASE_URL=postgresql://user:password@ep-xxx-pooler.region.aws.neon.tech/dbname?sslmode=require

# Direct (for migrations)
DATABASE_URL_DIRECT=postgresql://user:password@ep-xxx.region.aws.neon.tech/dbname?sslmode=require
```

### 7.2 SQLModel Settings for Neon

```python
from sqlalchemy.pool import NullPool

engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool,  # Disable SQLAlchemy pooling (Neon handles it)
    connect_args={
        "sslmode": "require",
        "connect_timeout": 10,
    }
)
```

### 7.3 Cold Start Handling

Neon may have cold starts. Handle connection errors:

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
)
def get_session():
    with Session(engine) as session:
        yield session
```

---

## 8. Environment Variables

### 8.1 Backend (.env)

```bash
# Neon PostgreSQL connection
DATABASE_URL=postgresql://user:password@ep-xxx.region.aws.neon.tech/dbname?sslmode=require

# Next.js URL for JWKS
AUTH_URL=http://localhost:3000
```

### 8.2 Frontend (.env)

```bash
# Same database for Better Auth
DATABASE_URL=postgresql://user:password@ep-xxx.region.aws.neon.tech/dbname?sslmode=require

# Better Auth secret
BETTER_AUTH_SECRET=<generated-secret>

# App URLs
NEXT_PUBLIC_APP_URL=http://localhost:3000
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

---

## 9. Security Considerations

### 9.1 SQL Injection Prevention

SQLModel (via SQLAlchemy) uses parameterized queries:

```python
# SAFE - parameterized
statement = select(Task).where(Task.user_id == user_id)

# UNSAFE - never do this
db.exec(text(f"SELECT * FROM tasks WHERE user_id = '{user_id}'"))
```

### 9.2 Data Isolation

All queries MUST include user_id filter:

```python
# CORRECT - always filter by user
select(Task).where(Task.id == task_id, Task.user_id == user.id)

# WRONG - missing user filter
select(Task).where(Task.id == task_id)
```

### 9.3 Sensitive Data

| Data | Protection |
|------|------------|
| DATABASE_URL | Environment variable only |
| User passwords | Handled by Better Auth (never in tasks DB) |
| Task content | Isolated by user_id |

---

## 10. Testing

### 10.1 Test Database

Use a separate test database or SQLite for testing:

```python
# conftest.py
import pytest
from sqlmodel import SQLModel, Session, create_engine
from sqlmodel.pool import StaticPool

@pytest.fixture
def session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
```

### 10.2 Test Helpers

```python
def create_test_task(session: Session, user_id: str = "test-user") -> Task:
    task = Task(
        user_id=user_id,
        title="Test Task",
        description="Test Description",
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    return task
```
