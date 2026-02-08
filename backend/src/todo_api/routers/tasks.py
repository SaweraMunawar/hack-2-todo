"""Task CRUD routes with Phase V advanced features."""

from datetime import datetime, timedelta, timezone
from typing import Literal, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, func, or_, select

from ..auth.jwt import CurrentUser, get_current_user
from ..database import get_session
from ..models import Task, TaskCreate, TaskListResponse, TaskRead, TaskUpdate

router = APIRouter(prefix="/api/v1/tasks", tags=["tasks"])


@router.get("", response_model=TaskListResponse)
async def list_tasks(
    user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_session),
    # Status filter
    completed: bool | None = None,
    status: Literal["all", "pending", "completed"] | None = None,
    # Phase V: Priority filter
    priority: Literal["high", "medium", "low"] | None = None,
    # Phase V: Tags filter (comma-separated)
    tags: str | None = None,
    # Phase V: Search
    search: str | None = None,
    # Phase V: Sort
    sort: Literal["due_date", "priority", "title", "created_at"] | None = None,
    order: Literal["asc", "desc"] = "desc",
    # Pagination
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    """List authenticated user's tasks with filtering, sorting, and search."""
    statement = select(Task).where(Task.user_id == user.id)

    # Status filter (new style takes precedence)
    if status == "pending":
        statement = statement.where(Task.completed == False)
    elif status == "completed":
        statement = statement.where(Task.completed == True)
    elif completed is not None:
        statement = statement.where(Task.completed == completed)

    # Priority filter
    if priority is not None:
        statement = statement.where(Task.priority == priority)

    # Tags filter (any matching tag)
    if tags is not None:
        tag_list = [t.strip() for t in tags.split(",") if t.strip()]
        if tag_list:
            # Filter tasks that have any of the specified tags
            # Using JSON contains for each tag with OR
            tag_conditions = []
            for tag in tag_list:
                # SQLAlchemy JSON contains check
                tag_conditions.append(Task.tags.contains([tag]))
            if tag_conditions:
                statement = statement.where(or_(*tag_conditions))

    # Search in title
    if search is not None and search.strip():
        search_term = f"%{search.strip().lower()}%"
        statement = statement.where(func.lower(Task.title).like(search_term))

    # Sorting
    if sort == "due_date":
        # Nulls last for due_date
        if order == "asc":
            statement = statement.order_by(Task.due_date.asc().nullslast())
        else:
            statement = statement.order_by(Task.due_date.desc().nullslast())
    elif sort == "priority":
        # Custom priority order: high > medium > low
        priority_order = func.case(
            (Task.priority == "high", 1),
            (Task.priority == "medium", 2),
            (Task.priority == "low", 3),
            else_=4,
        )
        if order == "asc":
            statement = statement.order_by(priority_order.desc())  # low first
        else:
            statement = statement.order_by(priority_order.asc())  # high first
    elif sort == "title":
        if order == "asc":
            statement = statement.order_by(func.lower(Task.title).asc())
        else:
            statement = statement.order_by(func.lower(Task.title).desc())
    else:
        # Default: created_at
        if order == "asc":
            statement = statement.order_by(Task.created_at.asc())
        else:
            statement = statement.order_by(Task.created_at.desc())

    statement = statement.offset(offset).limit(limit)
    tasks = db.exec(statement).all()

    # Count queries
    count_base = select(func.count()).select_from(Task).where(Task.user_id == user.id)
    total = db.exec(count_base).one()

    pending_count = db.exec(
        count_base.where(Task.completed == False)
    ).one()

    completed_count = db.exec(
        count_base.where(Task.completed == True)
    ).one()

    return TaskListResponse(
        tasks=tasks,
        total=total,
        pending_count=pending_count,
        completed_count=completed_count,
    )


@router.post("", response_model=TaskRead, status_code=201)
async def create_task(
    data: TaskCreate,
    user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """Create a new task for the authenticated user."""
    task = Task(
        user_id=user.id,
        title=data.title,
        description=data.description,
        priority=data.priority,
        tags=data.tags,
        due_date=data.due_date,
        recurring=data.recurring,
    )

    # Set reminder 1 hour before due date if due_date is set
    if data.due_date:
        task.reminder_at = data.due_date - timedelta(hours=1)

    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.get("/{task_id}", response_model=TaskRead)
async def get_task(
    task_id: UUID,
    user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """Get a specific task (must belong to user)."""
    statement = select(Task).where(Task.id == task_id, Task.user_id == user.id)
    task = db.exec(statement).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return task


@router.patch("/{task_id}", response_model=TaskRead)
async def update_task(
    task_id: UUID,
    data: TaskUpdate,
    user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """Update a task (partial update)."""
    statement = select(Task).where(Task.id == task_id, Task.user_id == user.id)
    task = db.exec(statement).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)

    # Update reminder if due_date changed
    if "due_date" in update_data and data.due_date:
        task.reminder_at = data.due_date - timedelta(hours=1)

    task.updated_at = datetime.now(timezone.utc)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}", status_code=204)
async def delete_task(
    task_id: UUID,
    user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """Delete a task."""
    statement = select(Task).where(Task.id == task_id, Task.user_id == user.id)
    task = db.exec(statement).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(task)
    db.commit()


@router.post("/{task_id}/toggle", response_model=TaskRead)
async def toggle_task(
    task_id: UUID,
    user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """Toggle task completion status. For recurring tasks, creates next occurrence."""
    statement = select(Task).where(Task.id == task_id, Task.user_id == user.id)
    task = db.exec(statement).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.completed = not task.completed
    task.updated_at = datetime.now(timezone.utc)

    # Handle recurring task completion
    if task.completed and task.recurring and task.due_date:
        next_due_date = calculate_next_due_date(task.due_date, task.recurring)
        next_task = Task(
            user_id=user.id,
            title=task.title,
            description=task.description,
            priority=task.priority,
            tags=task.tags,
            due_date=next_due_date,
            reminder_at=next_due_date - timedelta(hours=1) if next_due_date else None,
            recurring=task.recurring,
            recurring_parent_id=task.id,
        )
        db.add(next_task)

    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def calculate_next_due_date(current_due: datetime, pattern: str) -> datetime:
    """Calculate the next due date based on recurring pattern."""
    if pattern == "daily":
        return current_due + timedelta(days=1)
    elif pattern == "weekly":
        return current_due + timedelta(weeks=1)
    elif pattern == "monthly":
        # Add roughly a month (30 days)
        return current_due + timedelta(days=30)
    return current_due


# --- Phase V: Additional Endpoints ---


@router.patch("/{task_id}/priority", response_model=TaskRead)
async def update_priority(
    task_id: UUID,
    priority: Literal["high", "medium", "low"],
    user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """Update task priority."""
    statement = select(Task).where(Task.id == task_id, Task.user_id == user.id)
    task = db.exec(statement).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.priority = priority
    task.updated_at = datetime.now(timezone.utc)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.patch("/{task_id}/tags", response_model=TaskRead)
async def update_tags(
    task_id: UUID,
    action: Literal["add", "remove", "replace"],
    tags: list[str],
    user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """Update task tags."""
    statement = select(Task).where(Task.id == task_id, Task.user_id == user.id)
    task = db.exec(statement).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    current_tags = list(task.tags) if task.tags else []

    if action == "add":
        for tag in tags:
            if tag not in current_tags:
                current_tags.append(tag)
    elif action == "remove":
        current_tags = [t for t in current_tags if t not in tags]
    elif action == "replace":
        current_tags = tags

    task.tags = current_tags
    task.updated_at = datetime.now(timezone.utc)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.patch("/{task_id}/due-date", response_model=TaskRead)
async def update_due_date(
    task_id: UUID,
    due_date: Optional[datetime],
    set_reminder: bool = True,
    reminder_minutes_before: int = 60,
    user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """Update task due date and optionally set reminder."""
    statement = select(Task).where(Task.id == task_id, Task.user_id == user.id)
    task = db.exec(statement).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.due_date = due_date

    if due_date and set_reminder:
        task.reminder_at = due_date - timedelta(minutes=reminder_minutes_before)
    else:
        task.reminder_at = None

    task.updated_at = datetime.now(timezone.utc)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task
