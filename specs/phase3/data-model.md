# Phase III: Data Model Specification

## Overview
Phase III extends the Phase II data model with Conversation and Message tables for chat persistence.

## Existing Models (from Phase II)

### Task (unchanged)
| Field | Type | Constraints |
|-------|------|------------|
| id | UUID | Primary key, auto-generated |
| user_id | TEXT | Indexed, NOT NULL |
| title | VARCHAR(200) | NOT NULL, 1-200 chars |
| description | TEXT | Optional, max 1000 chars |
| completed | BOOLEAN | Default: false |
| created_at | TIMESTAMPTZ | UTC, auto-set |
| updated_at | TIMESTAMPTZ | Nullable, set on update |

## New Models

### Conversation
| Field | Type | Constraints |
|-------|------|------------|
| id | UUID | Primary key, auto-generated |
| user_id | TEXT | Indexed, NOT NULL |
| title | VARCHAR(200) | Optional, auto-generated from first message |
| created_at | TIMESTAMPTZ | UTC, auto-set |
| updated_at | TIMESTAMPTZ | Nullable, set on new message |

### Message
| Field | Type | Constraints |
|-------|------|------------|
| id | UUID | Primary key, auto-generated |
| conversation_id | UUID | Foreign key -> conversations.id, indexed |
| user_id | TEXT | NOT NULL |
| role | VARCHAR(20) | "user" or "assistant", NOT NULL |
| content | TEXT | NOT NULL |
| tool_calls | JSON | Nullable, stores tool invocation details |
| created_at | TIMESTAMPTZ | UTC, auto-set |

## SQLModel Definitions

```python
class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: str = Field(index=True, nullable=False)
    title: str = Field(default="", max_length=200)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = Field(default=None)


class Message(SQLModel, table=True):
    __tablename__ = "messages"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    conversation_id: UUID = Field(foreign_key="conversations.id", index=True)
    user_id: str = Field(nullable=False)
    role: str = Field(max_length=20)  # "user" or "assistant"
    content: str = Field(nullable=False)
    tool_calls: Optional[dict] = Field(default=None, sa_type=JSON)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
```

## Database Indexes
- `idx_conversations_user_id ON conversations(user_id)`
- `idx_messages_conversation_id ON messages(conversation_id)`
- `idx_messages_created_at ON messages(created_at)` (for ordering)

## API Schemas

### ChatRequest
```python
class ChatRequest(SQLModel):
    conversation_id: Optional[UUID] = None  # None = create new
    message: str = Field(min_length=1, max_length=2000)
```

### ChatResponse
```python
class ChatResponse(SQLModel):
    conversation_id: UUID
    response: str
    tool_calls: list[dict] = []
```

### ConversationRead
```python
class ConversationRead(SQLModel):
    id: UUID
    title: str
    created_at: datetime
    updated_at: Optional[datetime]
```
