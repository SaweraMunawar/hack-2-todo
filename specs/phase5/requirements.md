# Phase V: Advanced Cloud Deployment - Requirements

## Objective
Implement advanced features and deploy to production-grade Kubernetes with event-driven architecture using Kafka and Dapr.

## Part A: Advanced Features

### A1: Intermediate Level Features

#### Priorities
- Tasks support priority levels: high, medium, low
- Default priority: medium
- Visual indicators for priority in UI
- MCP tool support for setting priority via chat

#### Tags/Categories
- Tasks can have multiple tags (array of strings)
- Common tags: work, home, personal, urgent
- Filter tasks by one or more tags
- MCP tool support for adding/removing tags via chat

#### Search
- Full-text search by task title
- Search endpoint: GET /api/v1/tasks?search={keyword}
- MCP tool: search_tasks(query)

#### Filter
- Filter by status: all, pending, completed
- Filter by priority: high, medium, low
- Filter by tags: single or multiple
- Combined filters: status AND priority AND tags

#### Sort
- Sort by due date (ascending/descending)
- Sort by priority (high to low, low to high)
- Sort alphabetically (A-Z, Z-A)
- Sort by created date

### A2: Advanced Level Features

#### Recurring Tasks
- Recurrence patterns: daily, weekly, monthly
- When recurring task completed, auto-create next occurrence
- Recurring tasks have parent-child relationship
- MCP tool: create_recurring_task(title, pattern)

#### Due Dates
- Tasks can have due date with time
- Date/time picker in frontend
- MCP tool: set_due_date(task_id, date)
- Sort/filter by due date

#### Reminders
- Reminder events published when due date approaches
- Browser notifications for due tasks
- Configurable reminder time (e.g., 1 hour before, 1 day before)

### A3: Data Model Extensions

```sql
-- Task table extensions
ALTER TABLE tasks ADD COLUMN priority VARCHAR(10) DEFAULT 'medium';
ALTER TABLE tasks ADD COLUMN tags JSON DEFAULT '[]';
ALTER TABLE tasks ADD COLUMN due_date TIMESTAMPTZ;
ALTER TABLE tasks ADD COLUMN recurring VARCHAR(20);
ALTER TABLE tasks ADD COLUMN recurring_parent_id UUID REFERENCES tasks(id);
ALTER TABLE tasks ADD COLUMN reminder_at TIMESTAMPTZ;
```

### A4: New API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/v1/tasks?search={q} | Search tasks |
| GET | /api/v1/tasks?priority={p} | Filter by priority |
| GET | /api/v1/tasks?tags={t1,t2} | Filter by tags |
| GET | /api/v1/tasks?sort={field}&order={asc\|desc} | Sort tasks |
| PATCH | /api/v1/tasks/{id}/priority | Update priority |
| PATCH | /api/v1/tasks/{id}/tags | Update tags |
| PATCH | /api/v1/tasks/{id}/due-date | Set due date |
| POST | /api/v1/tasks/recurring | Create recurring task |

### A5: New MCP Tools

| Tool | Parameters | Description |
|------|------------|-------------|
| search_tasks | query: string | Search tasks by keyword |
| set_priority | task_id, priority | Set task priority |
| add_tag | task_id, tag | Add tag to task |
| remove_tag | task_id, tag | Remove tag from task |
| set_due_date | task_id, date | Set task due date |
| create_recurring | title, pattern | Create recurring task |
| filter_tasks | status, priority, tags | Filter tasks |
| sort_tasks | field, order | Sort tasks |

## Part B: Event-Driven Architecture (Kafka)

### B1: Kafka Topics

| Topic | Producer | Consumer | Purpose |
|-------|----------|----------|---------|
| task-events | Chat API (MCP Tools) | Audit Service, Recurring Task Service | All CRUD operations |
| reminders | Chat API | Notification Service | Scheduled reminder triggers |
| task-updates | Chat API | WebSocket Service | Real-time client sync |

### B2: Event Schemas

#### Task Event
```json
{
  "event_type": "created|updated|completed|deleted",
  "event_id": "uuid",
  "timestamp": "2024-01-15T10:30:00Z",
  "user_id": "user-uuid",
  "task_id": 123,
  "task_data": {
    "title": "Buy groceries",
    "completed": false,
    "priority": "high",
    "tags": ["home", "urgent"],
    "due_date": "2024-01-20T18:00:00Z"
  }
}
```

#### Reminder Event
```json
{
  "event_id": "uuid",
  "timestamp": "2024-01-15T10:30:00Z",
  "task_id": 123,
  "user_id": "user-uuid",
  "title": "Buy groceries",
  "due_at": "2024-01-20T18:00:00Z",
  "remind_at": "2024-01-20T17:00:00Z"
}
```

### B3: Microservices

#### Notification Service
- Consumes: reminders topic
- Function: Send browser push notifications
- Technology: FastAPI + web-push library

#### Recurring Task Service
- Consumes: task-events (completed events)
- Function: Create next occurrence of recurring tasks
- Technology: FastAPI + Kafka consumer

#### Audit Service
- Consumes: task-events (all events)
- Function: Store complete activity log
- Technology: FastAPI + database logging

## Part C: Dapr Integration

### C1: Dapr Building Blocks

| Block | Use Case |
|-------|----------|
| Pub/Sub | Kafka abstraction - publish/subscribe without Kafka client code |
| State Management | Conversation state storage |
| Service Invocation | Frontend-Backend communication with retries |
| Bindings | Cron triggers for scheduled reminder checks |
| Secrets Management | API keys, DB credentials |

### C2: Dapr Components

#### Pub/Sub Component (Kafka)
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    - name: brokers
      value: "your-cluster.cloud.redpanda.com:9092"
    - name: consumerGroup
      value: "todo-service"
    - name: authType
      value: "sasl"
    - name: saslUsername
      secretKeyRef:
        name: kafka-secrets
        key: username
    - name: saslPassword
      secretKeyRef:
        name: kafka-secrets
        key: password
```

#### State Store Component (PostgreSQL)
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
spec:
  type: state.postgresql
  version: v1
  metadata:
    - name: connectionString
      secretKeyRef:
        name: db-secrets
        key: connection-string
```

#### Cron Binding (Reminders)
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: reminder-cron
spec:
  type: bindings.cron
  version: v1
  metadata:
    - name: schedule
      value: "*/5 * * * *"
```

#### Secrets Store (Kubernetes)
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kubernetes-secrets
spec:
  type: secretstores.kubernetes
  version: v1
```

### C3: Dapr API Usage

#### Publishing Events (without Kafka library)
```python
import httpx

async def publish_task_event(event: dict):
    await httpx.post(
        "http://localhost:3500/v1.0/publish/kafka-pubsub/task-events",
        json=event
    )
```

#### State Management
```python
import httpx

async def save_conversation_state(conv_id: str, state: dict):
    await httpx.post(
        "http://localhost:3500/v1.0/state/statestore",
        json=[{"key": f"conv-{conv_id}", "value": state}]
    )

async def get_conversation_state(conv_id: str):
    response = await httpx.get(
        f"http://localhost:3500/v1.0/state/statestore/conv-{conv_id}"
    )
    return response.json()
```

#### Service Invocation
```javascript
// Frontend calling backend via Dapr
fetch("http://localhost:3500/v1.0/invoke/backend/method/api/v1/tasks")
```

## Part D: Cloud Deployment

### D1: Supported Platforms

| Platform | Description | Free Tier |
|----------|-------------|-----------|
| DigitalOcean DOKS | Managed Kubernetes | $200 credit for 60 days |
| Google Cloud GKE | Managed Kubernetes | $300 credit for 90 days |
| Azure AKS | Managed Kubernetes | $200 credit for 30 days |

### D2: CI/CD Pipeline (GitHub Actions)

#### Workflow: build-and-deploy.yml
```yaml
name: Build and Deploy

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build Backend Image
        run: docker build -f k8s/Dockerfile.backend -t $REGISTRY/todo-backend:$SHA ./backend
      - name: Build Frontend Image
        run: docker build -f k8s/Dockerfile.frontend -t $REGISTRY/todo-frontend:$SHA ./frontend
      - name: Push Images
        run: |
          docker push $REGISTRY/todo-backend:$SHA
          docker push $REGISTRY/todo-frontend:$SHA

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Deploy to Kubernetes
        run: |
          helm upgrade --install todo-backend k8s/helm/todo-backend --set image.tag=$SHA
          helm upgrade --install todo-frontend k8s/helm/todo-frontend --set image.tag=$SHA
```

### D3: Production Configuration

#### Backend Production values.yaml
```yaml
replicaCount: 2

resources:
  limits:
    cpu: 1000m
    memory: 1Gi
  requests:
    cpu: 500m
    memory: 512Mi

autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 5
  targetCPUUtilization: 70
```

#### Frontend Production values.yaml
```yaml
replicaCount: 2

service:
  type: LoadBalancer

resources:
  limits:
    cpu: 500m
    memory: 512Mi
  requests:
    cpu: 250m
    memory: 256Mi
```

### D4: Monitoring and Logging

- Kubernetes built-in metrics via `kubectl top`
- Pod logs via `kubectl logs`
- Health endpoints for uptime monitoring
- Optional: Prometheus + Grafana for metrics dashboard

## Technology Stack

| Component | Technology |
|-----------|-----------|
| Event Streaming | Kafka (Redpanda Cloud) |
| Distributed Runtime | Dapr |
| Cloud Kubernetes | DigitalOcean DOKS / GKE / AKS |
| CI/CD | GitHub Actions |
| Container Registry | DOCR / GCR / ACR |
| Monitoring | Kubernetes built-in / Prometheus |

## Environment Variables (New for Phase V)

```bash
# Kafka (Redpanda Cloud)
KAFKA_BOOTSTRAP_SERVERS=your-cluster.cloud.redpanda.com:9092
KAFKA_USERNAME=your-username
KAFKA_PASSWORD=your-password

# Dapr
DAPR_HTTP_PORT=3500

# Push Notifications (optional)
VAPID_PUBLIC_KEY=...
VAPID_PRIVATE_KEY=...
```

## Project Structure Extensions

```
k8s/
├── helm/
│   ├── todo-backend/
│   ├── todo-frontend/
│   ├── notification-service/     # New
│   ├── recurring-task-service/   # New
│   └── audit-service/            # New
├── dapr/
│   ├── components/
│   │   ├── kafka-pubsub.yaml
│   │   ├── statestore.yaml
│   │   ├── reminder-cron.yaml
│   │   └── secrets.yaml
│   └── config/
│       └── config.yaml
├── docker-compose.redpanda.yml   # Local Kafka
└── .github/
    └── workflows/
        └── deploy.yml
```
