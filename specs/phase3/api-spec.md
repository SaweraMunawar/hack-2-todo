# Phase III: API Specification

## Overview
Phase III adds a chat endpoint and conversation management to the existing Phase II API.

## Existing Endpoints (from Phase II - unchanged)
- `GET /api/v1/health` - Health check
- `GET /api/v1/tasks` - List tasks
- `POST /api/v1/tasks` - Create task
- `GET /api/v1/tasks/{id}` - Get task
- `PATCH /api/v1/tasks/{id}` - Update task
- `DELETE /api/v1/tasks/{id}` - Delete task
- `POST /api/v1/tasks/{id}/toggle` - Toggle completion

## New Endpoints

### POST /api/v1/chat
Send a chat message and get an AI response.

**Authentication**: Required (JWT Bearer token)

**Request Body**:
```json
{
  "conversation_id": "uuid-or-null",
  "message": "Add a task to buy groceries"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| conversation_id | UUID | No | Existing conversation (null = new) |
| message | string | Yes | User's natural language message (1-2000 chars) |

**Response** (200 OK):
```json
{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "response": "I've added \"Buy groceries\" to your task list!",
  "tool_calls": [
    {
      "tool": "add_task",
      "arguments": {"title": "Buy groceries"},
      "result": {"task_id": "...", "status": "created", "title": "Buy groceries"}
    }
  ]
}
```

**Error Responses**:
- `401 Unauthorized` - Missing/invalid JWT
- `404 Not Found` - Conversation not found or not owned by user
- `422 Validation Error` - Invalid request body
- `500 Internal Server Error` - AI processing failure

### GET /api/v1/conversations
List user's conversations.

**Authentication**: Required

**Response** (200 OK):
```json
{
  "conversations": [
    {
      "id": "uuid",
      "title": "Task management",
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T11:00:00Z"
    }
  ],
  "total": 1
}
```

### GET /api/v1/conversations/{id}/messages
Get messages for a conversation.

**Authentication**: Required

**Response** (200 OK):
```json
{
  "messages": [
    {
      "id": "uuid",
      "role": "user",
      "content": "Add a task to buy groceries",
      "tool_calls": null,
      "created_at": "2024-01-15T10:30:00Z"
    },
    {
      "id": "uuid",
      "role": "assistant",
      "content": "I've added \"Buy groceries\" to your task list!",
      "tool_calls": [{"tool": "add_task", "arguments": {...}, "result": {...}}],
      "created_at": "2024-01-15T10:30:01Z"
    }
  ]
}
```

## Stateless Request Flow

1. Receive POST /api/v1/chat with JWT token
2. Validate JWT, extract user_id
3. If conversation_id provided, verify ownership; else create new conversation
4. Fetch conversation history from database
5. Store user message in database
6. Build message array for OpenAI Agent (history + new message)
7. Run agent with MCP tools
8. Agent invokes appropriate MCP tool(s)
9. Store assistant response in database
10. Return response to client
11. Server holds NO state (ready for next request)
