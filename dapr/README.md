# Dapr Configuration

Dapr (Distributed Application Runtime) provides building blocks for microservices communication.

## Components

| Component | Type | Purpose |
|-----------|------|---------|
| kafka-pubsub | pubsub.kafka | Event streaming via Kafka/Redpanda |
| statestore | state.postgresql | State persistence |
| reminder-cron | bindings.cron | Scheduled reminder checks |
| kubernetes-secrets | secretstores.kubernetes | Secure secret access |

## Installation

### Install Dapr CLI

```bash
# Linux/macOS
curl -fsSL https://raw.githubusercontent.com/dapr/cli/master/install/install.sh | bash

# Windows (PowerShell)
powershell -Command "iwr -useb https://raw.githubusercontent.com/dapr/cli/master/install/install.ps1 | iex"
```

### Initialize Dapr

```bash
# Local (standalone mode)
dapr init

# Kubernetes
dapr init -k
```

## Local Development

### Start Redpanda (Kafka)

```bash
# From project root
docker compose -f docker-compose.redpanda.yml up -d
```

### Run Backend with Dapr

```bash
cd backend

# Run with Dapr sidecar
dapr run --app-id todo-backend --app-port 8000 --dapr-http-port 3500 \
  --resources-path ../dapr/components \
  -- uv run uvicorn todo_api.main:app --host 0.0.0.0 --port 8000
```

### View Dapr Dashboard

```bash
dapr dashboard
# Opens http://localhost:8080
```

## Kubernetes Deployment

### Apply Components

```bash
kubectl apply -f dapr/components/
kubectl apply -f dapr/config/
kubectl apply -f dapr/subscriptions/
```

### Create Secrets

```bash
# For Kafka cloud authentication
kubectl create secret generic kafka-secrets \
  --from-literal=brokers="your-cluster.cloud.redpanda.com:9092" \
  --from-literal=username="your-username" \
  --from-literal=password="your-password"
```

### Verify Installation

```bash
# Check Dapr status
dapr status -k

# List components
dapr components -k

# Check subscriptions
kubectl get subscriptions
```

## Topics

| Topic | Partitions | Retention | Purpose |
|-------|------------|-----------|---------|
| task-events | 3 | 7 days | All task CRUD operations |
| reminders | 1 | 1 day | Due date notifications |
| task-updates | 3 | 1 hour | Real-time UI updates |
| task-events-dlq | 1 | 30 days | Dead letter queue |

## Event Schemas

### task-events

```json
{
  "event_id": "uuid",
  "event_type": "created|updated|completed|deleted",
  "timestamp": "2024-01-15T10:30:00Z",
  "user_id": "user-uuid",
  "task_id": "task-uuid",
  "task_data": {
    "title": "Buy groceries",
    "completed": false,
    "priority": "high",
    "tags": ["home"],
    "due_date": "2024-01-20T18:00:00Z"
  },
  "metadata": {
    "source": "chat|api"
  }
}
```

## Configuration Files

```
dapr/
├── components/
│   ├── kafka-pubsub.yaml      # Local Kafka (Redpanda)
│   ├── kafka-pubsub-cloud.yaml # Cloud Kafka with SASL
│   ├── statestore.yaml        # PostgreSQL state store
│   ├── reminder-cron.yaml     # Cron for reminders
│   └── secrets.yaml           # K8s secrets access
├── config/
│   └── config.yaml            # Dapr configuration
├── subscriptions/
│   ├── task-events.yaml       # Task events subscription
│   ├── reminders.yaml         # Reminders subscription
│   └── task-updates.yaml      # Real-time updates subscription
└── README.md                  # This file
```

## Troubleshooting

### Check Sidecar Logs

```bash
# Local
dapr logs --app-id todo-backend

# Kubernetes
kubectl logs <pod-name> -c daprd
```

### Verify Component Status

```bash
# List running apps
dapr list

# Check component health
curl http://localhost:3500/v1.0/healthz
```
