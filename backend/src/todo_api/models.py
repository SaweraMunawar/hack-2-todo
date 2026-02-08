"""Task, Conversation, and Message models and schemas."""

from datetime import datetime, timezone
from enum import Enum
from typing import Literal, Optional
from uuid import UUID, uuid4

from pydantic import field_validator
from sqlalchemy import Column
from sqlalchemy import JSON as SA_JSON
from sqlmodel import Field, SQLModel


# --- Phase V: Enums ---


class Priority(str, Enum):
    """Task priority levels."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class RecurringPattern(str, Enum):
    """Recurring task patterns."""

    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


# --- Task Models ---


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
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = Field(default=None)

    # Phase V: Advanced features
    priority: str = Field(default="medium", max_length=10)
    tags: list[str] = Field(default=[], sa_column=Column(SA_JSON))
    due_date: Optional[datetime] = Field(default=None)
    reminder_at: Optional[datetime] = Field(default=None)
    recurring: Optional[str] = Field(default=None, max_length=20)
    recurring_parent_id: Optional[UUID] = Field(default=None, foreign_key="tasks.id")


class TaskCreate(TaskBase):
    """Schema for creating a task."""

    # Phase V fields
    priority: str = Field(default="medium")
    tags: list[str] = Field(default=[])
    due_date: Optional[datetime] = None
    recurring: Optional[str] = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Title cannot be empty")
        if len(v) > 200:
            raise ValueError("Title must be 200 characters or less")
        return v

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str) -> str:
        v = v.strip()
        if len(v) > 1000:
            raise ValueError("Description must be 1000 characters or less")
        return v

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v: str) -> str:
        if v not in ["high", "medium", "low"]:
            raise ValueError("Priority must be high, medium, or low")
        return v

    @field_validator("recurring")
    @classmethod
    def validate_recurring(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in ["daily", "weekly", "monthly"]:
            raise ValueError("Recurring must be daily, weekly, or monthly")
        return v


class TaskUpdate(SQLModel):
    """Schema for updating a task (all fields optional)."""

    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: Optional[bool] = None
    # Phase V fields
    priority: Optional[str] = None
    tags: Optional[list[str]] = None
    due_date: Optional[datetime] = None
    recurring: Optional[str] = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("Title cannot be empty")
            if len(v) > 200:
                raise ValueError("Title must be 200 characters or less")
        return v

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if len(v) > 1000:
                raise ValueError("Description must be 1000 characters or less")
        return v

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in ["high", "medium", "low"]:
            raise ValueError("Priority must be high, medium, or low")
        return v

    @field_validator("recurring")
    @classmethod
    def validate_recurring(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in ["daily", "weekly", "monthly"]:
            raise ValueError("Recurring must be daily, weekly, or monthly")
        return v


class TaskRead(TaskBase):
    """Schema for reading a task."""

    id: UUID
    completed: bool
    created_at: datetime
    updated_at: Optional[datetime]
    # Phase V fields
    priority: str
    tags: list[str]
    due_date: Optional[datetime]
    recurring: Optional[str]
    recurring_parent_id: Optional[UUID]


class TaskListResponse(SQLModel):
    """Response schema for task list."""

    tasks: list[TaskRead]
    total: int
    pending_count: int = 0
    completed_count: int = 0


# --- Phase III: Conversation & Message Models ---


class Conversation(SQLModel, table=True):
    """Conversation database model."""

    __tablename__ = "conversations"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: str = Field(index=True, nullable=False)
    title: str = Field(default="", max_length=200)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = Field(default=None)


class Message(SQLModel, table=True):
    """Message database model."""

    __tablename__ = "messages"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    conversation_id: UUID = Field(foreign_key="conversations.id", index=True)
    user_id: str = Field(nullable=False)
    role: str = Field(max_length=20)  # "user" or "assistant"
    content: str = Field(nullable=False)
    tool_calls: Optional[dict] = Field(default=None, sa_type=SA_JSON)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# --- Phase III: Chat Schemas ---


class ChatRequest(SQLModel):
    """Schema for chat request."""

    conversation_id: Optional[UUID] = None
    message: str = Field(min_length=1, max_length=2000)


class ChatResponse(SQLModel):
    """Schema for chat response."""

    conversation_id: UUID
    response: str
    tool_calls: list[dict] = []


class ConversationRead(SQLModel):
    """Schema for reading a conversation."""

    id: UUID
    title: str
    created_at: datetime
    updated_at: Optional[datetime]


class ConversationListResponse(SQLModel):
    """Response schema for conversation list."""

    conversations: list[ConversationRead]
    total: int


class MessageRead(SQLModel):
    """Schema for reading a message."""

    id: UUID
    role: str
    content: str
    tool_calls: Optional[dict] = None
    created_at: datetime


class MessageListResponse(SQLModel):
    """Response schema for message list."""

    messages: list[MessageRead]


# --- Phase V: Audit Log Model ---


class AuditLog(SQLModel, table=True):
    """Audit log for tracking all task operations."""

    __tablename__ = "audit_log"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    event_id: UUID = Field(default_factory=uuid4, unique=True)
    event_type: str = Field(max_length=50)  # created, updated, completed, deleted
    user_id: str = Field(index=True)
    task_id: Optional[UUID] = Field(default=None)
    task_data: Optional[dict] = Field(default=None, sa_column=Column(SA_JSON))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), index=True)
    source: Optional[str] = Field(default=None, max_length=100)  # api, chat, recurring-service
