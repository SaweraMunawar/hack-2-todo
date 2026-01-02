"""Task manager for in-memory task storage and operations.

This module provides the TaskManager class that handles all CRUD operations
as specified in specs/phase1/data-model.md section 3.
"""

from datetime import datetime

from .models import Task


class TaskManager:
    """In-memory task storage and operations.

    Manages a collection of tasks with CRUD operations. Tasks are stored
    in memory and will not persist across application restarts.

    Attributes:
        _tasks: Dictionary mapping task IDs to Task objects
        _next_id: Counter for generating unique task IDs
    """

    def __init__(self) -> None:
        """Initialize an empty task manager."""
        self._tasks: dict[int, Task] = {}
        self._next_id: int = 1

    def add(self, title: str, description: str = "") -> Task:
        """Create and store a new task.

        Args:
            title: The task title (should be pre-validated)
            description: The task description (default: empty string)

        Returns:
            The newly created Task object
        """
        task = Task(
            id=self._next_id,
            title=title,
            description=description,
            completed=False,
            created_at=datetime.now(),
            updated_at=None,
        )
        self._tasks[task.id] = task
        self._next_id += 1
        return task

    def get_all(self) -> list[Task]:
        """Return all tasks ordered by ID.

        Returns:
            List of all tasks, sorted by ID (ascending)
            Returns empty list if no tasks exist
        """
        return sorted(self._tasks.values(), key=lambda t: t.id)

    def get(self, task_id: int) -> Task | None:
        """Return a task by its ID.

        Args:
            task_id: The ID of the task to retrieve

        Returns:
            The Task object if found, None otherwise
        """
        return self._tasks.get(task_id)

    def update(
        self,
        task_id: int,
        title: str | None = None,
        description: str | None = None,
    ) -> bool:
        """Update a task's title and/or description.

        Args:
            task_id: The ID of the task to update
            title: New title (None to keep current)
            description: New description (None to keep current)

        Returns:
            True if the task was updated, False if task not found
        """
        task = self._tasks.get(task_id)
        if task is None:
            return False

        if title is not None:
            task.title = title
        if description is not None:
            task.description = description

        task.updated_at = datetime.now()
        return True

    def delete(self, task_id: int) -> bool:
        """Remove a task by its ID.

        Note: The ID will not be reused for future tasks.

        Args:
            task_id: The ID of the task to delete

        Returns:
            True if the task was deleted, False if task not found
        """
        if task_id in self._tasks:
            del self._tasks[task_id]
            return True
        return False

    def toggle_complete(self, task_id: int) -> bool:
        """Toggle the completion status of a task.

        If the task is pending, it becomes complete.
        If the task is complete, it becomes pending.

        Args:
            task_id: The ID of the task to toggle

        Returns:
            True if the task was toggled, False if task not found
        """
        task = self._tasks.get(task_id)
        if task is None:
            return False

        task.completed = not task.completed
        task.updated_at = datetime.now()
        return True

    def get_ids(self) -> set[int]:
        """Return the set of all existing task IDs.

        Returns:
            Set of task IDs for validation purposes
        """
        return set(self._tasks.keys())

    def get_stats(self) -> dict[str, int]:
        """Return statistics about the tasks.

        Returns:
            Dictionary with keys: 'total', 'completed', 'pending'
        """
        tasks = list(self._tasks.values())
        total = len(tasks)
        completed = sum(1 for t in tasks if t.completed)
        return {
            "total": total,
            "completed": completed,
            "pending": total - completed,
        }

    def is_empty(self) -> bool:
        """Check if there are no tasks.

        Returns:
            True if no tasks exist, False otherwise
        """
        return len(self._tasks) == 0
