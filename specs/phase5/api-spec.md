# Phase V: API Specification

## Extended Task Endpoints

### GET /api/v1/tasks

Extended with filtering, sorting, and search capabilities.

#### Query Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| status | string | Filter by status: all, pending, completed |
| priority | string | Filter by priority: high, medium, low |
| tags | string | Comma-separated list of tags |
| search | string | Search keyword in title |
| sort | string | Sort field: due_date, priority, title, created_at |
| order | string | Sort order: asc, desc (default: asc) |
| limit | integer | Number of results (default: 50, max: 100) |
| offset | integer | Offset for pagination (default: 0) |

#### Example Requests

```bash
# Get all pending high-priority tasks
GET /api/v1/tasks?status=pending&priority=high

# Search for tasks containing "groceries"
GET /api/v1/tasks?search=groceries

# Get tasks tagged with "work" sorted by due date
GET /api/v1/tasks?tags=work&sort=due_date&order=asc

# Combined filters
GET /api/v1/tasks?status=pending&priority=high&tags=work,urgent&sort=due_date
```

#### Response

```json
{
  "tasks": [
    {
      "id": 1,
      "title": "Buy groceries",
      "completed": false,
      "priority": "high",
      "tags": ["home", "urgent"],
      "due_date": "2024-01-20T18:00:00Z",
      "recurring": null,
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total": 1,
  "pending_count": 1,
  "completed_count": 0
}
```

### POST /api/v1/tasks

Extended to support new fields.

#### Request Body

```json
{
  "title": "Weekly team meeting",
  "priority": "high",
  "tags": ["work", "meetings"],
  "due_date": "2024-01-22T10:00:00Z",
  "recurring": "weekly"
}
```

#### Response

```json
{
  "id": 2,
  "title": "Weekly team meeting",
  "completed": false,
  "priority": "high",
  "tags": ["work", "meetings"],
  "due_date": "2024-01-22T10:00:00Z",
  "recurring": "weekly",
  "recurring_parent_id": null,
  "created_at": "2024-01-15T11:00:00Z",
  "updated_at": "2024-01-15T11:00:00Z"
}
```

### PATCH /api/v1/tasks/{id}

Extended to support priority, tags, due_date, and recurring.

#### Request Body

```json
{
  "priority": "medium",
  "tags": ["work"],
  "due_date": "2024-01-25T10:00:00Z"
}
```

### PATCH /api/v1/tasks/{id}/priority

Set task priority.

#### Request Body

```json
{
  "priority": "high"
}
```

#### Response

```json
{
  "id": 1,
  "title": "Buy groceries",
  "priority": "high",
  "message": "Priority updated to high"
}
```

### PATCH /api/v1/tasks/{id}/tags

Add or remove tags.

#### Request Body (Add Tags)

```json
{
  "action": "add",
  "tags": ["urgent", "important"]
}
```

#### Request Body (Remove Tags)

```json
{
  "action": "remove",
  "tags": ["urgent"]
}
```

#### Request Body (Replace Tags)

```json
{
  "action": "replace",
  "tags": ["work", "priority"]
}
```

### PATCH /api/v1/tasks/{id}/due-date

Set or update due date.

#### Request Body

```json
{
  "due_date": "2024-01-20T18:00:00Z",
  "set_reminder": true,
  "reminder_minutes_before": 60
}
```

### POST /api/v1/tasks/recurring

Create a recurring task.

#### Request Body

```json
{
  "title": "Daily standup",
  "priority": "high",
  "tags": ["work", "meetings"],
  "due_date": "2024-01-16T09:00:00Z",
  "recurring": "daily"
}
```

## Push Notification Endpoints

### POST /api/v1/push/subscribe

Subscribe to push notifications.

#### Request Body

```json
{
  "endpoint": "https://fcm.googleapis.com/...",
  "keys": {
    "p256dh": "...",
    "auth": "..."
  }
}
```

#### Response

```json
{
  "message": "Subscription created",
  "subscription_id": 1
}
```

### DELETE /api/v1/push/unsubscribe

Unsubscribe from push notifications.

#### Request Body

```json
{
  "endpoint": "https://fcm.googleapis.com/..."
}
```

## Audit Log Endpoints

### GET /api/v1/audit

Get audit log for current user.

#### Query Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| task_id | integer | Filter by task ID |
| event_type | string | Filter by event type |
| from | datetime | Start date |
| to | datetime | End date |
| limit | integer | Number of results (default: 50) |
| offset | integer | Offset for pagination |

#### Response

```json
{
  "events": [
    {
      "event_id": "550e8400-e29b-41d4-a716-446655440000",
      "event_type": "created",
      "task_id": 1,
      "task_data": {
        "title": "Buy groceries",
        "priority": "high"
      },
      "timestamp": "2024-01-15T10:30:00Z",
      "source": "chat"
    }
  ],
  "total": 1
}
```

## Dapr Service Invocation Endpoints

When Dapr is enabled, services can be invoked via the Dapr sidecar.

### Service Discovery

| Service | Dapr App ID | Endpoints |
|---------|-------------|-----------|
| Backend | todo-backend | /api/v1/* |
| Notification | notification-service | /notify |
| Recurring Task | recurring-service | /process |
| Audit | audit-service | /log |

### Example Dapr Invocation

```bash
# Via Dapr sidecar
curl http://localhost:3500/v1.0/invoke/todo-backend/method/api/v1/tasks

# Direct (within cluster)
curl http://todo-backend:8000/api/v1/tasks
```

## Error Responses

### 400 Bad Request

```json
{
  "detail": "Invalid priority value. Must be high, medium, or low."
}
```

### 404 Not Found

```json
{
  "detail": "Task not found"
}
```

### 422 Unprocessable Entity

```json
{
  "detail": [
    {
      "loc": ["body", "priority"],
      "msg": "value is not a valid enumeration member",
      "type": "type_error.enum"
    }
  ]
}
```

## Rate Limiting

| Endpoint | Limit |
|----------|-------|
| POST /api/v1/tasks | 100 requests/minute |
| GET /api/v1/tasks | 200 requests/minute |
| POST /api/v1/chat | 30 requests/minute |

## Webhook Events (Future)

For integrations, webhooks can be configured:

| Event | Payload |
|-------|---------|
| task.created | Task object |
| task.completed | Task object |
| task.deleted | { task_id, title } |
| reminder.due | Reminder object |
