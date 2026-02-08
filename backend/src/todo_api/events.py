"""Event publishing for Dapr/Kafka integration - Phase V."""

import os
from datetime import datetime, timezone
from typing import Literal, Optional
from uuid import UUID, uuid4

import httpx

# Dapr sidecar configuration
DAPR_HTTP_PORT = int(os.getenv("DAPR_HTTP_PORT", 3500))
DAPR_URL = f"http://localhost:{DAPR_HTTP_PORT}"
PUBSUB_NAME = "kafka-pubsub"

# Feature flag to enable/disable events
EVENTS_ENABLED = os.getenv("EVENTS_ENABLED", "false").lower() == "true"


async def publish_event(topic: str, event: dict) -> bool:
    """Publish an event to a Kafka topic via Dapr.

    Args:
        topic: The topic name (e.g., "task-events")
        event: The event payload

    Returns:
        True if published successfully, False otherwise
    """
    if not EVENTS_ENABLED:
        return True  # Skip if events disabled

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{DAPR_URL}/v1.0/publish/{PUBSUB_NAME}/{topic}",
                json=event,
                headers={"Content-Type": "application/json"},
                timeout=5.0,
            )
            return response.status_code in (200, 204)
    except httpx.RequestError:
        # Log error but don't fail the request
        return False


async def publish_task_event(
    event_type: Literal["created", "updated", "completed", "deleted"],
    user_id: str,
    task_id: UUID,
    task_data: Optional[dict] = None,
    source: str = "api",
) -> bool:
    """Publish a task event to the task-events topic.

    Args:
        event_type: Type of event
        user_id: The user who performed the action
        task_id: The task ID
        task_data: Optional task data snapshot
        source: Source of the event ("api" or "chat")

    Returns:
        True if published successfully
    """
    event = {
        "event_id": str(uuid4()),
        "event_type": event_type,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "user_id": user_id,
        "task_id": str(task_id),
        "task_data": task_data or {},
        "metadata": {
            "source": source,
        },
    }
    return await publish_event("task-events", event)


async def publish_reminder_event(
    task_id: UUID,
    user_id: str,
    title: str,
    due_at: datetime,
    remind_at: datetime,
    reminder_type: str = "1_hour_before",
) -> bool:
    """Publish a reminder event to the reminders topic.

    Args:
        task_id: The task ID
        user_id: The user who owns the task
        title: Task title
        due_at: When the task is due
        remind_at: When to send the reminder
        reminder_type: Type of reminder

    Returns:
        True if published successfully
    """
    event = {
        "event_id": str(uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "task_id": str(task_id),
        "user_id": user_id,
        "title": title,
        "due_at": due_at.isoformat(),
        "remind_at": remind_at.isoformat(),
        "reminder_type": reminder_type,
    }
    return await publish_event("reminders", event)


async def publish_task_update(
    update_type: Literal["created", "updated", "deleted"],
    user_id: str,
    task: dict,
) -> bool:
    """Publish a real-time task update for connected clients.

    Args:
        update_type: Type of update
        user_id: The user who owns the task
        task: Task data for the UI

    Returns:
        True if published successfully
    """
    event = {
        "event_id": str(uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "user_id": user_id,
        "update_type": update_type,
        "task": task,
    }
    return await publish_event("task-updates", event)


# Dapr subscription endpoint for programmatic subscriptions
def get_subscriptions() -> list[dict]:
    """Return Dapr subscription configuration.

    This can be used if programmatic subscriptions are preferred
    over declarative YAML subscriptions.
    """
    return [
        {
            "pubsubname": PUBSUB_NAME,
            "topic": "task-events",
            "route": "/events/task",
        },
        {
            "pubsubname": PUBSUB_NAME,
            "topic": "reminders",
            "route": "/events/reminder",
        },
    ]
