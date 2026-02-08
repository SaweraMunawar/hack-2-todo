# Phase III: MCP Server Specification

## Overview
The MCP (Model Context Protocol) server exposes task CRUD operations as tools that the OpenAI Agent can invoke to manage the user's todo list.

## MCP Server Configuration
- Built with Official MCP SDK for Python (`mcp`)
- Runs as an in-process server (stdio transport within FastAPI)
- All tools receive user_id from the authenticated session
- Tools are stateless - all state in database

## MCP Tools

### Tool: add_task
**Purpose**: Create a new task

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| user_id | string | Yes | Authenticated user ID |
| title | string | Yes | Task title (1-200 chars) |
| description | string | No | Task description (max 1000 chars) |

**Returns**:
```json
{"task_id": "uuid", "status": "created", "title": "Buy groceries"}
```

### Tool: list_tasks
**Purpose**: Retrieve tasks from the list

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| user_id | string | Yes | Authenticated user ID |
| status | string | No | Filter: "all", "pending", "completed" (default: "all") |

**Returns**:
```json
[
  {"id": "uuid", "title": "Buy groceries", "completed": false, "description": ""},
  {"id": "uuid", "title": "Call mom", "completed": true, "description": ""}
]
```

### Tool: complete_task
**Purpose**: Mark a task as complete

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| user_id | string | Yes | Authenticated user ID |
| task_id | string | Yes | UUID of the task |

**Returns**:
```json
{"task_id": "uuid", "status": "completed", "title": "Call mom"}
```

**Error**: `{"error": "Task not found"}` if task doesn't exist or wrong user

### Tool: delete_task
**Purpose**: Remove a task from the list

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| user_id | string | Yes | Authenticated user ID |
| task_id | string | Yes | UUID of the task |

**Returns**:
```json
{"task_id": "uuid", "status": "deleted", "title": "Old task"}
```

### Tool: update_task
**Purpose**: Modify task title or description

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| user_id | string | Yes | Authenticated user ID |
| task_id | string | Yes | UUID of the task |
| title | string | No | New title |
| description | string | No | New description |

**Returns**:
```json
{"task_id": "uuid", "status": "updated", "title": "Buy groceries and fruits"}
```

## Agent Behavior Specification

| User Intent | Agent Action |
|-------------|-------------|
| Adding/creating/remembering something | Call `add_task` |
| See/show/list tasks | Call `list_tasks` with appropriate filter |
| Done/complete/finished | Call `complete_task` |
| Delete/remove/cancel | Call `delete_task` |
| Change/update/rename | Call `update_task` |
| Ambiguous reference (e.g., "delete the meeting task") | Call `list_tasks` first, then target tool |

## Agent System Prompt
```
You are a helpful todo list assistant. You help users manage their tasks through natural language.

Available tools:
- add_task: Create a new task
- list_tasks: View tasks (filter by status: all, pending, completed)
- complete_task: Mark a task as done
- delete_task: Remove a task
- update_task: Change task title or description

Rules:
1. Always confirm actions with a friendly response
2. When the user refers to a task by name but not ID, list tasks first to find the right one
3. Be concise but helpful
4. If a tool returns an error, explain it to the user
5. You can chain multiple tools in one turn if needed
```

## Natural Language Examples

| User Says | Agent Should Do |
|-----------|----------------|
| "Add a task to buy groceries" | `add_task(title="Buy groceries")` |
| "Show me all my tasks" | `list_tasks(status="all")` |
| "What's pending?" | `list_tasks(status="pending")` |
| "Mark task 3 as complete" | `complete_task(task_id=...)` |
| "Delete the meeting task" | `list_tasks()` -> find match -> `delete_task(task_id=...)` |
| "Change task 1 to 'Call mom tonight'" | `update_task(task_id=..., title="Call mom tonight")` |
| "I need to remember to pay bills" | `add_task(title="Pay bills")` |
| "What have I completed?" | `list_tasks(status="completed")` |

## Implementation Notes
- The MCP tools interact directly with the database via SQLModel
- user_id is injected from the JWT-authenticated session, NOT from the AI agent
- Tool results are returned to the agent for natural language response generation
- Tool errors (e.g., task not found) should be handled gracefully
