"""MCP task tools for the AI agent - Phase V with advanced features."""

from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

from sqlmodel import Session, func, or_, select

from ..database import engine
from ..models import Task


def add_task(
    user_id: str,
    title: str,
    description: str = "",
    priority: str = "medium",
    tags: list[str] | None = None,
    due_date: str | None = None,
    recurring: str | None = None,
) -> dict:
    """Create a new task with optional priority, tags, due date, and recurring pattern.

    Args:
        user_id: The user's ID
        title: Task title
        description: Task description (optional)
        priority: Priority level - "high", "medium", or "low" (default: "medium")
        tags: List of tags like ["work", "urgent"] (optional)
        due_date: ISO format datetime string like "2024-01-20T18:00:00Z" (optional)
        recurring: Recurring pattern - "daily", "weekly", or "monthly" (optional)

    Returns:
        dict with task_id, status, and title
    """
    with Session(engine) as session:
        # Parse due_date if provided
        parsed_due_date = None
        reminder_at = None
        if due_date:
            try:
                parsed_due_date = datetime.fromisoformat(due_date.replace("Z", "+00:00"))
                reminder_at = parsed_due_date - timedelta(hours=1)
            except ValueError:
                return {"error": f"Invalid due_date format: {due_date}. Use ISO format."}

        # Validate priority
        if priority not in ["high", "medium", "low"]:
            priority = "medium"

        # Validate recurring
        if recurring and recurring not in ["daily", "weekly", "monthly"]:
            recurring = None

        task = Task(
            user_id=user_id,
            title=title,
            description=description,
            priority=priority,
            tags=tags or [],
            due_date=parsed_due_date,
            reminder_at=reminder_at,
            recurring=recurring,
        )
        session.add(task)
        session.commit()
        session.refresh(task)

        result = {
            "task_id": str(task.id),
            "status": "created",
            "title": task.title,
            "priority": task.priority,
        }
        if task.tags:
            result["tags"] = task.tags
        if task.due_date:
            result["due_date"] = task.due_date.isoformat()
        if task.recurring:
            result["recurring"] = task.recurring

        return result


def list_tasks(
    user_id: str,
    status: str = "all",
    priority: str | None = None,
    tags: list[str] | None = None,
    search: str | None = None,
    sort_by: str | None = None,
    limit: int = 20,
) -> list[dict]:
    """List tasks with optional filters and search.

    Args:
        user_id: The user's ID
        status: Filter by status - "all", "pending", or "completed"
        priority: Filter by priority - "high", "medium", or "low"
        tags: Filter by tags (any matching tag)
        search: Search keyword in title
        sort_by: Sort by - "due_date", "priority", "title", or "created_at"
        limit: Maximum number of tasks to return (default: 20)

    Returns:
        list of task dictionaries
    """
    with Session(engine) as session:
        statement = select(Task).where(Task.user_id == user_id)

        # Status filter
        if status == "pending":
            statement = statement.where(Task.completed == False)  # noqa: E712
        elif status == "completed":
            statement = statement.where(Task.completed == True)  # noqa: E712

        # Priority filter
        if priority and priority in ["high", "medium", "low"]:
            statement = statement.where(Task.priority == priority)

        # Tags filter
        if tags:
            tag_conditions = [Task.tags.contains([tag]) for tag in tags]
            statement = statement.where(or_(*tag_conditions))

        # Search
        if search:
            search_term = f"%{search.lower()}%"
            statement = statement.where(func.lower(Task.title).like(search_term))

        # Sorting
        if sort_by == "due_date":
            statement = statement.order_by(Task.due_date.asc().nullslast())
        elif sort_by == "priority":
            priority_order = func.case(
                (Task.priority == "high", 1),
                (Task.priority == "medium", 2),
                (Task.priority == "low", 3),
                else_=4,
            )
            statement = statement.order_by(priority_order.asc())
        elif sort_by == "title":
            statement = statement.order_by(func.lower(Task.title).asc())
        else:
            statement = statement.order_by(Task.created_at.desc())

        statement = statement.limit(limit)
        tasks = session.exec(statement).all()

        return [
            {
                "id": str(t.id),
                "title": t.title,
                "completed": t.completed,
                "description": t.description,
                "priority": t.priority,
                "tags": t.tags or [],
                "due_date": t.due_date.isoformat() if t.due_date else None,
                "recurring": t.recurring,
            }
            for t in tasks
        ]


def search_tasks(user_id: str, query: str) -> list[dict]:
    """Search tasks by keyword in title.

    Args:
        user_id: The user's ID
        query: Search keyword

    Returns:
        list of matching task dictionaries
    """
    return list_tasks(user_id, search=query)


def complete_task(user_id: str, task_id: str) -> dict:
    """Mark a task as complete. For recurring tasks, creates the next occurrence.

    Args:
        user_id: The user's ID
        task_id: The task ID to complete

    Returns:
        dict with completion status and next task info if recurring
    """
    with Session(engine) as session:
        statement = select(Task).where(
            Task.id == UUID(task_id), Task.user_id == user_id
        )
        task = session.exec(statement).first()
        if not task:
            return {"error": "Task not found"}

        task.completed = True
        task.updated_at = datetime.now(timezone.utc)

        result = {"task_id": str(task.id), "status": "completed", "title": task.title}

        # Handle recurring task
        if task.recurring and task.due_date:
            next_due_date = calculate_next_due_date(task.due_date, task.recurring)
            next_task = Task(
                user_id=user_id,
                title=task.title,
                description=task.description,
                priority=task.priority,
                tags=task.tags,
                due_date=next_due_date,
                reminder_at=next_due_date - timedelta(hours=1),
                recurring=task.recurring,
                recurring_parent_id=task.id,
            )
            session.add(next_task)
            session.add(task)
            session.commit()
            session.refresh(next_task)
            result["next_task_id"] = str(next_task.id)
            result["next_due_date"] = next_due_date.isoformat()
            result["message"] = f"Task completed. Next occurrence created for {next_due_date.strftime('%Y-%m-%d')}"
        else:
            session.add(task)
            session.commit()

        return result


def delete_task(user_id: str, task_id: str) -> dict:
    """Delete a task.

    Args:
        user_id: The user's ID
        task_id: The task ID to delete

    Returns:
        dict with deletion status
    """
    with Session(engine) as session:
        statement = select(Task).where(
            Task.id == UUID(task_id), Task.user_id == user_id
        )
        task = session.exec(statement).first()
        if not task:
            return {"error": "Task not found"}
        title = task.title
        session.delete(task)
        session.commit()
        return {"task_id": task_id, "status": "deleted", "title": title}


def update_task(
    user_id: str,
    task_id: str,
    title: str | None = None,
    description: str | None = None,
    priority: str | None = None,
    tags: list[str] | None = None,
    due_date: str | None = None,
    recurring: str | None = None,
) -> dict:
    """Update a task's properties.

    Args:
        user_id: The user's ID
        task_id: The task ID to update
        title: New title (optional)
        description: New description (optional)
        priority: New priority - "high", "medium", or "low" (optional)
        tags: New tags list (replaces existing) (optional)
        due_date: New due date in ISO format (optional)
        recurring: New recurring pattern (optional)

    Returns:
        dict with update status
    """
    with Session(engine) as session:
        statement = select(Task).where(
            Task.id == UUID(task_id), Task.user_id == user_id
        )
        task = session.exec(statement).first()
        if not task:
            return {"error": "Task not found"}

        if title is not None:
            task.title = title
        if description is not None:
            task.description = description
        if priority is not None and priority in ["high", "medium", "low"]:
            task.priority = priority
        if tags is not None:
            task.tags = tags
        if due_date is not None:
            try:
                task.due_date = datetime.fromisoformat(due_date.replace("Z", "+00:00"))
                task.reminder_at = task.due_date - timedelta(hours=1)
            except ValueError:
                return {"error": f"Invalid due_date format: {due_date}"}
        if recurring is not None:
            if recurring in ["daily", "weekly", "monthly", ""]:
                task.recurring = recurring if recurring else None
            else:
                return {"error": f"Invalid recurring pattern: {recurring}"}

        task.updated_at = datetime.now(timezone.utc)
        session.add(task)
        session.commit()
        session.refresh(task)

        return {
            "task_id": str(task.id),
            "status": "updated",
            "title": task.title,
            "priority": task.priority,
            "tags": task.tags,
            "due_date": task.due_date.isoformat() if task.due_date else None,
        }


def set_priority(user_id: str, task_id: str, priority: str) -> dict:
    """Set task priority.

    Args:
        user_id: The user's ID
        task_id: The task ID
        priority: Priority level - "high", "medium", or "low"

    Returns:
        dict with update status
    """
    if priority not in ["high", "medium", "low"]:
        return {"error": f"Invalid priority: {priority}. Must be high, medium, or low."}

    with Session(engine) as session:
        statement = select(Task).where(
            Task.id == UUID(task_id), Task.user_id == user_id
        )
        task = session.exec(statement).first()
        if not task:
            return {"error": "Task not found"}

        task.priority = priority
        task.updated_at = datetime.now(timezone.utc)
        session.add(task)
        session.commit()

        return {
            "task_id": str(task.id),
            "status": "updated",
            "title": task.title,
            "priority": task.priority,
        }


def add_tag(user_id: str, task_id: str, tag: str) -> dict:
    """Add a tag to a task.

    Args:
        user_id: The user's ID
        task_id: The task ID
        tag: Tag to add

    Returns:
        dict with update status and current tags
    """
    with Session(engine) as session:
        statement = select(Task).where(
            Task.id == UUID(task_id), Task.user_id == user_id
        )
        task = session.exec(statement).first()
        if not task:
            return {"error": "Task not found"}

        current_tags = list(task.tags) if task.tags else []
        if tag not in current_tags:
            current_tags.append(tag)
            task.tags = current_tags
            task.updated_at = datetime.now(timezone.utc)
            session.add(task)
            session.commit()

        return {
            "task_id": str(task.id),
            "status": "updated",
            "title": task.title,
            "tags": current_tags,
        }


def remove_tag(user_id: str, task_id: str, tag: str) -> dict:
    """Remove a tag from a task.

    Args:
        user_id: The user's ID
        task_id: The task ID
        tag: Tag to remove

    Returns:
        dict with update status and current tags
    """
    with Session(engine) as session:
        statement = select(Task).where(
            Task.id == UUID(task_id), Task.user_id == user_id
        )
        task = session.exec(statement).first()
        if not task:
            return {"error": "Task not found"}

        current_tags = list(task.tags) if task.tags else []
        if tag in current_tags:
            current_tags.remove(tag)
            task.tags = current_tags
            task.updated_at = datetime.now(timezone.utc)
            session.add(task)
            session.commit()

        return {
            "task_id": str(task.id),
            "status": "updated",
            "title": task.title,
            "tags": current_tags,
        }


def set_due_date(user_id: str, task_id: str, due_date: str) -> dict:
    """Set or update task due date.

    Args:
        user_id: The user's ID
        task_id: The task ID
        due_date: Due date in ISO format (e.g., "2024-01-20T18:00:00Z")

    Returns:
        dict with update status
    """
    try:
        parsed_date = datetime.fromisoformat(due_date.replace("Z", "+00:00"))
    except ValueError:
        return {"error": f"Invalid due_date format: {due_date}. Use ISO format."}

    with Session(engine) as session:
        statement = select(Task).where(
            Task.id == UUID(task_id), Task.user_id == user_id
        )
        task = session.exec(statement).first()
        if not task:
            return {"error": "Task not found"}

        task.due_date = parsed_date
        task.reminder_at = parsed_date - timedelta(hours=1)
        task.updated_at = datetime.now(timezone.utc)
        session.add(task)
        session.commit()

        return {
            "task_id": str(task.id),
            "status": "updated",
            "title": task.title,
            "due_date": task.due_date.isoformat(),
            "reminder_at": task.reminder_at.isoformat(),
        }


def create_recurring_task(
    user_id: str,
    title: str,
    pattern: str,
    due_date: str,
    description: str = "",
    priority: str = "medium",
    tags: list[str] | None = None,
) -> dict:
    """Create a recurring task.

    Args:
        user_id: The user's ID
        title: Task title
        pattern: Recurring pattern - "daily", "weekly", or "monthly"
        due_date: First due date in ISO format
        description: Task description (optional)
        priority: Priority level (optional)
        tags: Tags list (optional)

    Returns:
        dict with task creation status
    """
    if pattern not in ["daily", "weekly", "monthly"]:
        return {"error": f"Invalid pattern: {pattern}. Must be daily, weekly, or monthly."}

    return add_task(
        user_id=user_id,
        title=title,
        description=description,
        priority=priority,
        tags=tags,
        due_date=due_date,
        recurring=pattern,
    )


def calculate_next_due_date(current_due: datetime, pattern: str) -> datetime:
    """Calculate the next due date based on recurring pattern."""
    if pattern == "daily":
        return current_due + timedelta(days=1)
    elif pattern == "weekly":
        return current_due + timedelta(weeks=1)
    elif pattern == "monthly":
        return current_due + timedelta(days=30)
    return current_due
