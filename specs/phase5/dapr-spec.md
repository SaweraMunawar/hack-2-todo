# Phase V: Dapr Specification

## Overview

Dapr (Distributed Application Runtime) provides building blocks for microservices, abstracting infrastructure details behind simple HTTP/gRPC APIs.

## Building Blocks Used

| Block | Purpose | Component Type |
|-------|---------|----------------|
| Pub/Sub | Event streaming | pubsub.kafka |
| State Management | Conversation state | state.postgresql |
| Service Invocation | Inter-service calls | Built-in |
| Bindings | Cron triggers | bindings.cron |
| Secrets | Credential management | secretstores.kubernetes |

## Installation

### Install Dapr CLI

```bash
# Linux/macOS
curl -fsSL https://raw.githubusercontent.com/dapr/cli/master/install/install.sh | bash

# Windows
powershell -Command "iwr -useb https://raw.githubusercontent.com/dapr/cli/master/install/install.ps1 | iex"
```

### Initialize Dapr on Kubernetes

```bash
# Initialize with Kubernetes mode
dapr init -k

# Verify installation
dapr status -k
kubectl get pods -n dapr-system
```

## Component Configurations

### Pub/Sub Component (Kafka)

```yaml
# dapr/components/kafka-pubsub.yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
  namespace: default
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    # Broker configuration
    - name: brokers
      value: "your-cluster.cloud.redpanda.com:9092"
    - name: consumerGroup
      value: "todo-app"

    # Authentication (for cloud)
    - name: authType
      value: "sasl"
    - name: saslMechanism
      value: "SCRAM-SHA-256"
    - name: saslUsername
      secretKeyRef:
        name: kafka-secrets
        key: username
    - name: saslPassword
      secretKeyRef:
        name: kafka-secrets
        key: password

    # TLS
    - name: tls
      value: "true"

    # Consumer settings
    - name: maxMessageBytes
      value: "1048576"
    - name: consumeRetryInterval
      value: "100ms"
```

### State Store Component (PostgreSQL)

```yaml
# dapr/components/statestore.yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
  namespace: default
spec:
  type: state.postgresql
  version: v1
  metadata:
    - name: connectionString
      secretKeyRef:
        name: db-secrets
        key: connection-string
    - name: tableName
      value: "dapr_state"
    - name: keyPrefix
      value: "none"
```

### Cron Binding (Reminders)

```yaml
# dapr/components/reminder-cron.yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: reminder-cron
  namespace: default
spec:
  type: bindings.cron
  version: v1
  metadata:
    - name: schedule
      value: "*/5 * * * *"  # Every 5 minutes
```

### Secrets Store (Kubernetes)

```yaml
# dapr/components/secrets.yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kubernetes-secrets
  namespace: default
spec:
  type: secretstores.kubernetes
  version: v1
```

## Dapr Configuration

```yaml
# dapr/config/config.yaml
apiVersion: dapr.io/v1alpha1
kind: Configuration
metadata:
  name: todo-config
  namespace: default
spec:
  tracing:
    samplingRate: "1"
    zipkin:
      endpointAddress: "http://zipkin:9411/api/v2/spans"

  mtls:
    enabled: true

  accessControl:
    defaultAction: allow
    trustDomain: "todo-app"
```

## Application Integration

### Enabling Dapr Sidecar

Add annotations to Kubernetes deployment:

```yaml
# In deployment.yaml
spec:
  template:
    metadata:
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "todo-backend"
        dapr.io/app-port: "8000"
        dapr.io/config: "todo-config"
```

### Python Code Examples

#### Publishing Events

```python
# Without Dapr (direct Kafka)
from kafka import KafkaProducer
producer = KafkaProducer(...)
producer.send("task-events", value=event)

# With Dapr (HTTP API)
import httpx

DAPR_PORT = int(os.getenv("DAPR_HTTP_PORT", 3500))

async def publish_task_event(event: dict):
    async with httpx.AsyncClient() as client:
        await client.post(
            f"http://localhost:{DAPR_PORT}/v1.0/publish/kafka-pubsub/task-events",
            json=event
        )
```

#### Subscribing to Events

```python
# Dapr will call this endpoint when events arrive
from fastapi import FastAPI

app = FastAPI()

@app.post("/events/task")
async def handle_task_event(event: dict):
    """Called by Dapr when task-events messages arrive."""
    event_type = event.get("data", {}).get("event_type")

    if event_type == "completed":
        await handle_task_completed(event["data"])

    return {"status": "ok"}

# Subscription configuration (declarative)
# dapr/subscriptions/task-events.yaml
```

#### State Management

```python
import httpx

DAPR_PORT = int(os.getenv("DAPR_HTTP_PORT", 3500))
STATE_STORE = "statestore"

async def save_state(key: str, value: dict):
    async with httpx.AsyncClient() as client:
        await client.post(
            f"http://localhost:{DAPR_PORT}/v1.0/state/{STATE_STORE}",
            json=[{"key": key, "value": value}]
        )

async def get_state(key: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"http://localhost:{DAPR_PORT}/v1.0/state/{STATE_STORE}/{key}"
        )
        return response.json() if response.status_code == 200 else None

async def delete_state(key: str):
    async with httpx.AsyncClient() as client:
        await client.delete(
            f"http://localhost:{DAPR_PORT}/v1.0/state/{STATE_STORE}/{key}"
        )

# Usage
await save_state(f"conversation-{conv_id}", {"messages": messages})
state = await get_state(f"conversation-{conv_id}")
```

#### Service Invocation

```python
import httpx

DAPR_PORT = int(os.getenv("DAPR_HTTP_PORT", 3500))

async def invoke_service(app_id: str, method: str, data: dict = None):
    async with httpx.AsyncClient() as client:
        url = f"http://localhost:{DAPR_PORT}/v1.0/invoke/{app_id}/method/{method}"
        if data:
            response = await client.post(url, json=data)
        else:
            response = await client.get(url)
        return response.json()

# Usage: Call notification service
await invoke_service("notification-service", "notify", {
    "user_id": user_id,
    "title": "Task Due",
    "message": f"Task '{task_title}' is due soon"
})
```

#### Input Binding (Cron)

```python
# Dapr will call this endpoint based on cron schedule
@app.post("/reminder-cron")
async def check_reminders():
    """Called by Dapr every 5 minutes (cron binding)."""
    # Query pending reminders
    pending = await get_pending_reminders()

    for reminder in pending:
        if reminder.remind_at <= datetime.utcnow():
            await send_notification(reminder)
            await mark_reminder_sent(reminder.id)

    return {"processed": len(pending)}
```

#### Secrets Access

```python
import httpx

DAPR_PORT = int(os.getenv("DAPR_HTTP_PORT", 3500))

async def get_secret(store: str, key: str) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"http://localhost:{DAPR_PORT}/v1.0/secrets/{store}/{key}"
        )
        secrets = response.json()
        return secrets.get(key)

# Usage
openai_key = await get_secret("kubernetes-secrets", "openai-api-key")
```

## Subscriptions

### Declarative Subscriptions

```yaml
# dapr/subscriptions/task-events.yaml
apiVersion: dapr.io/v1alpha1
kind: Subscription
metadata:
  name: task-events-sub
spec:
  pubsubname: kafka-pubsub
  topic: task-events
  route: /events/task
scopes:
  - audit-service
  - recurring-service
```

```yaml
# dapr/subscriptions/reminders.yaml
apiVersion: dapr.io/v1alpha1
kind: Subscription
metadata:
  name: reminders-sub
spec:
  pubsubname: kafka-pubsub
  topic: reminders
  route: /events/reminder
scopes:
  - notification-service
```

### Programmatic Subscriptions

```python
# Return subscription info at startup
@app.get("/dapr/subscribe")
async def subscribe():
    return [
        {
            "pubsubname": "kafka-pubsub",
            "topic": "task-events",
            "route": "/events/task"
        }
    ]
```

## Deployment Annotations

### Backend Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: todo-backend
spec:
  template:
    metadata:
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "todo-backend"
        dapr.io/app-port: "8000"
        dapr.io/config: "todo-config"
        dapr.io/log-level: "info"
        dapr.io/enable-api-logging: "true"
```

### Notification Service Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: notification-service
spec:
  template:
    metadata:
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "notification-service"
        dapr.io/app-port: "8001"
        dapr.io/config: "todo-config"
```

## Local Development

### Run with Dapr

```bash
# Run backend with Dapr sidecar
dapr run --app-id todo-backend --app-port 8000 --dapr-http-port 3500 \
  -- uvicorn todo_api.main:app --host 0.0.0.0 --port 8000

# Run with components directory
dapr run --app-id todo-backend --app-port 8000 \
  --resources-path ./dapr/components \
  -- uvicorn todo_api.main:app --host 0.0.0.0 --port 8000
```

### View Dapr Dashboard

```bash
dapr dashboard
# Opens http://localhost:8080
```

## Troubleshooting

### Check Sidecar Status

```bash
# List running Dapr apps
dapr list

# Check sidecar logs
kubectl logs <pod-name> -c daprd

# Check component status
dapr components -k
```

### Common Issues

| Issue | Solution |
|-------|----------|
| Sidecar not starting | Check annotations, verify dapr init -k completed |
| Can't connect to component | Verify component YAML is applied, check secrets |
| Pub/Sub not working | Check subscription scopes, verify topic exists |
| State store errors | Check PostgreSQL connection string, table permissions |

## Benefits Summary

| Without Dapr | With Dapr |
|--------------|-----------|
| kafka-python, redis-py, psycopg2 libraries | Single HTTP API |
| Connection strings in code | YAML component config |
| Manual retry logic | Built-in retries, circuit breakers |
| Service URLs hardcoded | Automatic service discovery |
| Secrets in env vars | Secure secret stores |
| Tight infrastructure coupling | Swap Kafka for RabbitMQ with config change |
