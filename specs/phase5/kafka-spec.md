# Phase V: Kafka Specification

## Overview

Kafka provides event-driven architecture for the Todo application, enabling decoupled microservices communication.

## Kafka Service Recommendations

### For Cloud Deployment

| Service | Free Tier | Recommendation |
|---------|-----------|----------------|
| Redpanda Cloud | Free Serverless tier | **Primary choice** - Kafka-compatible, no Zookeeper |
| Confluent Cloud | $400 credit for 30 days | Industry standard, good docs |
| CloudKarafka | "Developer Duck" free plan | Simple, 5 topics free |

### For Local Development

| Option | Complexity | Description |
|--------|------------|-------------|
| Redpanda Docker | Easy | Single binary, Kafka-compatible |
| Bitnami Kafka Helm | Medium | Kubernetes-native |
| Strimzi Operator | Hard | Production-grade K8s operator |

## Topics

### task-events

All task CRUD operations are published to this topic.

| Field | Type | Description |
|-------|------|-------------|
| Name | task-events | |
| Partitions | 3 | Based on user_id hash |
| Retention | 7 days | |
| Consumers | Audit Service, Recurring Task Service | |

#### Event Schema

```json
{
  "event_id": "uuid",
  "event_type": "created|updated|completed|deleted",
  "timestamp": "2024-01-15T10:30:00Z",
  "user_id": "user-uuid",
  "task_id": 123,
  "task_data": {
    "title": "Buy groceries",
    "completed": false,
    "priority": "high",
    "tags": ["home"],
    "due_date": "2024-01-20T18:00:00Z",
    "recurring": null
  },
  "metadata": {
    "source": "chat|api",
    "correlation_id": "request-uuid"
  }
}
```

### reminders

Scheduled reminder events for due tasks.

| Field | Type | Description |
|-------|------|-------------|
| Name | reminders | |
| Partitions | 1 | Order matters for reminders |
| Retention | 1 day | Short-lived events |
| Consumers | Notification Service | |

#### Event Schema

```json
{
  "event_id": "uuid",
  "timestamp": "2024-01-15T10:30:00Z",
  "task_id": 123,
  "user_id": "user-uuid",
  "title": "Buy groceries",
  "due_at": "2024-01-20T18:00:00Z",
  "remind_at": "2024-01-20T17:00:00Z",
  "reminder_type": "1_hour_before|1_day_before"
}
```

### task-updates

Real-time task updates for connected clients.

| Field | Type | Description |
|-------|------|-------------|
| Name | task-updates | |
| Partitions | 3 | Based on user_id hash |
| Retention | 1 hour | Very short-lived |
| Consumers | WebSocket Service | |

#### Event Schema

```json
{
  "event_id": "uuid",
  "timestamp": "2024-01-15T10:30:00Z",
  "user_id": "user-uuid",
  "update_type": "created|updated|deleted",
  "task": {
    "id": 123,
    "title": "Buy groceries",
    "completed": false,
    "priority": "high"
  }
}
```

## Producer Configuration

### Python Producer (Direct Kafka)

```python
from kafka import KafkaProducer
import json

producer = KafkaProducer(
    bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
    security_protocol="SASL_SSL",
    sasl_mechanism="SCRAM-SHA-256",
    sasl_plain_username=settings.KAFKA_USERNAME,
    sasl_plain_password=settings.KAFKA_PASSWORD,
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    key_serializer=lambda k: k.encode('utf-8') if k else None,
    acks='all',
    retries=3
)

def publish_task_event(event: dict, user_id: str):
    producer.send(
        "task-events",
        key=user_id,  # Partition by user
        value=event
    )
    producer.flush()
```

### Python Producer (via Dapr)

```python
import httpx

DAPR_URL = "http://localhost:3500"

async def publish_task_event(event: dict):
    await httpx.post(
        f"{DAPR_URL}/v1.0/publish/kafka-pubsub/task-events",
        json=event,
        headers={"Content-Type": "application/json"}
    )
```

## Consumer Configuration

### Python Consumer (Direct Kafka)

```python
from kafka import KafkaConsumer
import json

consumer = KafkaConsumer(
    "task-events",
    bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
    security_protocol="SASL_SSL",
    sasl_mechanism="SCRAM-SHA-256",
    sasl_plain_username=settings.KAFKA_USERNAME,
    sasl_plain_password=settings.KAFKA_PASSWORD,
    group_id="audit-service",
    auto_offset_reset="earliest",
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

for message in consumer:
    event = message.value
    process_event(event)
```

### Dapr Subscription

```yaml
# subscription.yaml
apiVersion: dapr.io/v1alpha1
kind: Subscription
metadata:
  name: task-events-subscription
spec:
  topic: task-events
  route: /events/task
  pubsubname: kafka-pubsub
scopes:
  - audit-service
  - recurring-service
```

```python
# FastAPI handler
@app.post("/events/task")
async def handle_task_event(event: dict):
    event_type = event.get("event_type")
    if event_type == "completed":
        await process_completed_task(event)
    # Log to audit
    await log_audit_event(event)
```

## Local Development Setup

### docker-compose.redpanda.yml

```yaml
version: '3.8'

services:
  redpanda:
    image: redpandadata/redpanda:latest
    container_name: redpanda
    command:
      - redpanda start
      - --smp 1
      - --memory 512M
      - --overprovisioned
      - --kafka-addr PLAINTEXT://0.0.0.0:9092
      - --advertise-kafka-addr PLAINTEXT://localhost:9092
      - --pandaproxy-addr PLAINTEXT://0.0.0.0:8082
      - --advertise-pandaproxy-addr PLAINTEXT://localhost:8082
    ports:
      - "9092:9092"
      - "8081:8081"  # Schema Registry
      - "8082:8082"  # REST Proxy
      - "9644:9644"  # Admin API
    volumes:
      - redpanda-data:/var/lib/redpanda/data

  console:
    image: redpandadata/console:latest
    container_name: redpanda-console
    entrypoint: /bin/sh
    command: -c "echo \"$$CONSOLE_CONFIG_FILE\" > /tmp/config.yml && /app/console"
    environment:
      CONFIG_FILEPATH: /tmp/config.yml
      CONSOLE_CONFIG_FILE: |
        kafka:
          brokers: ["redpanda:9092"]
        redpanda:
          adminApi:
            enabled: true
            urls: ["http://redpanda:9644"]
    ports:
      - "8080:8080"
    depends_on:
      - redpanda

volumes:
  redpanda-data:
```

### Create Topics

```bash
# Using Redpanda CLI (rpk)
docker exec -it redpanda rpk topic create task-events --partitions 3
docker exec -it redpanda rpk topic create reminders --partitions 1
docker exec -it redpanda rpk topic create task-updates --partitions 3

# Using kafka CLI
kafka-topics.sh --create --topic task-events \
  --bootstrap-server localhost:9092 \
  --partitions 3 --replication-factor 1
```

## Cloud Setup (Redpanda Cloud)

1. Sign up at https://redpanda.com/cloud
2. Create a Serverless cluster
3. Create topics: task-events, reminders, task-updates
4. Get credentials:
   - Bootstrap server URL
   - SASL username
   - SASL password

### Environment Variables

```bash
KAFKA_BOOTSTRAP_SERVERS=your-cluster.cloud.redpanda.com:9092
KAFKA_USERNAME=your-username
KAFKA_PASSWORD=your-password
KAFKA_SECURITY_PROTOCOL=SASL_SSL
KAFKA_SASL_MECHANISM=SCRAM-SHA-256
```

## Monitoring

### Redpanda Console

Access at http://localhost:8080 for local development.

Features:
- View topics and messages
- Consumer group lag
- Broker health

### Key Metrics

| Metric | Alert Threshold |
|--------|-----------------|
| Consumer lag | > 1000 messages |
| Message rate | < 1 msg/sec (if expected traffic) |
| Error rate | > 1% |
| Partition distribution | Uneven by > 20% |

## Error Handling

### Dead Letter Queue

Failed messages are sent to a dead letter topic for manual review.

```python
DLQ_TOPIC = "task-events-dlq"

async def process_with_dlq(message):
    try:
        await process_event(message)
    except Exception as e:
        # Send to DLQ
        await producer.send(
            DLQ_TOPIC,
            value={
                "original_message": message,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        )
```

### Retry Logic

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10)
)
async def publish_event(event: dict):
    await producer.send("task-events", value=event)
```
