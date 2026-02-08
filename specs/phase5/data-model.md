# Phase V: Data Model Specification

## Extended Task Model

### Task Table Schema

```sql
CREATE TABLE tasks (
    -- Existing columns (Phase II)
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    completed BOOLEAN DEFAULT FALSE,
    user_id VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- New columns (Phase V)
    priority VARCHAR(10) DEFAULT 'medium',
    tags JSON DEFAULT '[]',
    due_date TIMESTAMPTZ,
    reminder_at TIMESTAMPTZ,
    recurring VARCHAR(20),
    recurring_parent_id INTEGER REFERENCES tasks(id)
);

-- Indexes for filtering and sorting
CREATE INDEX idx_tasks_priority ON tasks(priority);
CREATE INDEX idx_tasks_due_date ON tasks(due_date);
CREATE INDEX idx_tasks_user_completed ON tasks(user_id, completed);
```

### Priority Enum Values
| Value | Description |
|-------|-------------|
| high | Urgent/important tasks |
| medium | Normal priority (default) |
| low | Can be done later |

### Recurring Enum Values
| Value | Description | Next Occurrence |
|-------|-------------|-----------------|
| daily | Repeats every day | +1 day |
| weekly | Repeats every week | +7 days |
| monthly | Repeats every month | +1 month |

### SQLModel Definition

```python
from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel, Column, JSON

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    # Existing fields
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=500)
    completed: bool = Field(default=False)
    user_id: str = Field(max_length=255, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # New fields (Phase V)
    priority: str = Field(default="medium", max_length=10)
    tags: list[str] = Field(default=[], sa_column=Column(JSON))
    due_date: Optional[datetime] = Field(default=None)
    reminder_at: Optional[datetime] = Field(default=None)
    recurring: Optional[str] = Field(default=None, max_length=20)
    recurring_parent_id: Optional[int] = Field(
        default=None,
        foreign_key="tasks.id"
    )
```

## Audit Log Model

### Audit Table Schema

```sql
CREATE TABLE audit_log (
    id SERIAL PRIMARY KEY,
    event_id UUID NOT NULL UNIQUE,
    event_type VARCHAR(50) NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    task_id INTEGER,
    task_data JSON,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    source VARCHAR(100)
);

CREATE INDEX idx_audit_user ON audit_log(user_id);
CREATE INDEX idx_audit_timestamp ON audit_log(timestamp);
CREATE INDEX idx_audit_task ON audit_log(task_id);
```

### SQLModel Definition

```python
from datetime import datetime
from typing import Optional
from uuid import UUID
from sqlmodel import Field, SQLModel, Column, JSON

class AuditLog(SQLModel, table=True):
    __tablename__ = "audit_log"

    id: Optional[int] = Field(default=None, primary_key=True)
    event_id: UUID = Field(unique=True)
    event_type: str = Field(max_length=50)  # created, updated, completed, deleted
    user_id: str = Field(max_length=255, index=True)
    task_id: Optional[int] = Field(default=None)
    task_data: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    timestamp: datetime = Field(default_factory=datetime.utcnow, index=True)
    source: Optional[str] = Field(default=None, max_length=100)  # api, chat, recurring-service
```

## Reminder Queue Model

### Reminder Table Schema

```sql
CREATE TABLE reminder_queue (
    id SERIAL PRIMARY KEY,
    task_id INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    user_id VARCHAR(255) NOT NULL,
    remind_at TIMESTAMPTZ NOT NULL,
    sent BOOLEAN DEFAULT FALSE,
    sent_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_reminder_pending ON reminder_queue(remind_at) WHERE sent = FALSE;
CREATE INDEX idx_reminder_user ON reminder_queue(user_id);
```

### SQLModel Definition

```python
from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel

class ReminderQueue(SQLModel, table=True):
    __tablename__ = "reminder_queue"

    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: int = Field(foreign_key="tasks.id")
    user_id: str = Field(max_length=255, index=True)
    remind_at: datetime = Field(index=True)
    sent: bool = Field(default=False)
    sent_at: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

## Push Subscription Model (for Browser Notifications)

### Push Subscription Table Schema

```sql
CREATE TABLE push_subscriptions (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    endpoint TEXT NOT NULL,
    p256dh TEXT NOT NULL,
    auth TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, endpoint)
);

CREATE INDEX idx_push_user ON push_subscriptions(user_id);
```

### SQLModel Definition

```python
from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel

class PushSubscription(SQLModel, table=True):
    __tablename__ = "push_subscriptions"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(max_length=255, index=True)
    endpoint: str
    p256dh: str
    auth: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

## Pydantic Schemas

### Request Schemas

```python
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    priority: str = Field(default="medium", pattern="^(high|medium|low)$")
    tags: list[str] = Field(default=[])
    due_date: Optional[datetime] = None
    recurring: Optional[str] = Field(default=None, pattern="^(daily|weekly|monthly)$")

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    completed: Optional[bool] = None
    priority: Optional[str] = Field(None, pattern="^(high|medium|low)$")
    tags: Optional[list[str]] = None
    due_date: Optional[datetime] = None
    recurring: Optional[str] = Field(None, pattern="^(daily|weekly|monthly)$")

class TaskFilter(BaseModel):
    status: Optional[str] = Field(None, pattern="^(all|pending|completed)$")
    priority: Optional[str] = Field(None, pattern="^(high|medium|low)$")
    tags: Optional[list[str]] = None
    search: Optional[str] = None
    sort_by: Optional[str] = Field(None, pattern="^(due_date|priority|title|created_at)$")
    sort_order: Optional[str] = Field(default="asc", pattern="^(asc|desc)$")
```

### Response Schemas

```python
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class TaskResponse(BaseModel):
    id: int
    title: str
    completed: bool
    priority: str
    tags: list[str]
    due_date: Optional[datetime]
    recurring: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class TaskListResponse(BaseModel):
    tasks: list[TaskResponse]
    total: int
    pending_count: int
    completed_count: int
```

## Migration Script

```sql
-- Phase V Migration: Add advanced task features

-- Add priority column
ALTER TABLE tasks
ADD COLUMN IF NOT EXISTS priority VARCHAR(10) DEFAULT 'medium';

-- Add tags column
ALTER TABLE tasks
ADD COLUMN IF NOT EXISTS tags JSON DEFAULT '[]';

-- Add due_date column
ALTER TABLE tasks
ADD COLUMN IF NOT EXISTS due_date TIMESTAMPTZ;

-- Add reminder_at column
ALTER TABLE tasks
ADD COLUMN IF NOT EXISTS reminder_at TIMESTAMPTZ;

-- Add recurring column
ALTER TABLE tasks
ADD COLUMN IF NOT EXISTS recurring VARCHAR(20);

-- Add recurring_parent_id column
ALTER TABLE tasks
ADD COLUMN IF NOT EXISTS recurring_parent_id INTEGER REFERENCES tasks(id);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_tasks_priority ON tasks(priority);
CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON tasks(due_date);
CREATE INDEX IF NOT EXISTS idx_tasks_user_completed ON tasks(user_id, completed);

-- Create audit_log table
CREATE TABLE IF NOT EXISTS audit_log (
    id SERIAL PRIMARY KEY,
    event_id UUID NOT NULL UNIQUE,
    event_type VARCHAR(50) NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    task_id INTEGER,
    task_data JSON,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    source VARCHAR(100)
);

-- Create reminder_queue table
CREATE TABLE IF NOT EXISTS reminder_queue (
    id SERIAL PRIMARY KEY,
    task_id INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    user_id VARCHAR(255) NOT NULL,
    remind_at TIMESTAMPTZ NOT NULL,
    sent BOOLEAN DEFAULT FALSE,
    sent_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create push_subscriptions table
CREATE TABLE IF NOT EXISTS push_subscriptions (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    endpoint TEXT NOT NULL,
    p256dh TEXT NOT NULL,
    auth TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, endpoint)
);
```
