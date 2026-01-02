"""Tests for TaskManager class."""

import pytest
from datetime import datetime

from todo.manager import TaskManager


class TestTaskManagerAdd:
    """Tests for TaskManager.add method."""

    def test_add_creates_task(self):
        """Test that add creates a task with correct attributes."""
        manager = TaskManager()
        task = manager.add("Buy groceries")

        assert task.id == 1
        assert task.title == "Buy groceries"
        assert task.description == ""
        assert task.completed is False

    def test_add_with_description(self):
        """Test that add accepts description."""
        manager = TaskManager()
        task = manager.add("Buy groceries", "Get milk and eggs")

        assert task.title == "Buy groceries"
        assert task.description == "Get milk and eggs"

    def test_add_increments_id(self):
        """Test that each add increments the ID."""
        manager = TaskManager()
        task1 = manager.add("Task 1")
        task2 = manager.add("Task 2")
        task3 = manager.add("Task 3")

        assert task1.id == 1
        assert task2.id == 2
        assert task3.id == 3

    def test_add_sets_created_at(self):
        """Test that add sets created_at timestamp."""
        manager = TaskManager()
        before = datetime.now()
        task = manager.add("Task")
        after = datetime.now()

        assert before <= task.created_at <= after


class TestTaskManagerGetAll:
    """Tests for TaskManager.get_all method."""

    def test_get_all_empty(self):
        """Test get_all returns empty list when no tasks."""
        manager = TaskManager()
        tasks = manager.get_all()

        assert tasks == []

    def test_get_all_returns_all_tasks(self):
        """Test get_all returns all added tasks."""
        manager = TaskManager()
        manager.add("Task 1")
        manager.add("Task 2")
        manager.add("Task 3")

        tasks = manager.get_all()
        assert len(tasks) == 3

    def test_get_all_ordered_by_id(self):
        """Test get_all returns tasks ordered by ID."""
        manager = TaskManager()
        manager.add("Task 1")
        manager.add("Task 2")
        manager.add("Task 3")

        tasks = manager.get_all()
        assert [t.id for t in tasks] == [1, 2, 3]


class TestTaskManagerGet:
    """Tests for TaskManager.get method."""

    def test_get_returns_task(self):
        """Test get returns the correct task."""
        manager = TaskManager()
        manager.add("Task 1")
        task2 = manager.add("Task 2")

        result = manager.get(2)
        assert result == task2

    def test_get_returns_none_for_missing(self):
        """Test get returns None for nonexistent ID."""
        manager = TaskManager()
        manager.add("Task 1")

        result = manager.get(99)
        assert result is None


class TestTaskManagerUpdate:
    """Tests for TaskManager.update method."""

    def test_update_title(self):
        """Test updating task title."""
        manager = TaskManager()
        manager.add("Old title")

        result = manager.update(1, title="New title")

        assert result is True
        assert manager.get(1).title == "New title"

    def test_update_description(self):
        """Test updating task description."""
        manager = TaskManager()
        manager.add("Title", "Old desc")

        result = manager.update(1, description="New desc")

        assert result is True
        assert manager.get(1).description == "New desc"

    def test_update_both(self):
        """Test updating both title and description."""
        manager = TaskManager()
        manager.add("Old title", "Old desc")

        result = manager.update(1, title="New title", description="New desc")

        assert result is True
        task = manager.get(1)
        assert task.title == "New title"
        assert task.description == "New desc"

    def test_update_sets_updated_at(self):
        """Test that update sets updated_at timestamp."""
        manager = TaskManager()
        manager.add("Title")

        before = datetime.now()
        manager.update(1, title="New title")
        after = datetime.now()

        task = manager.get(1)
        assert task.updated_at is not None
        assert before <= task.updated_at <= after

    def test_update_missing_returns_false(self):
        """Test update returns False for nonexistent ID."""
        manager = TaskManager()

        result = manager.update(99, title="New")
        assert result is False


class TestTaskManagerDelete:
    """Tests for TaskManager.delete method."""

    def test_delete_removes_task(self):
        """Test that delete removes the task."""
        manager = TaskManager()
        manager.add("Task 1")
        manager.add("Task 2")

        result = manager.delete(1)

        assert result is True
        assert manager.get(1) is None
        assert len(manager.get_all()) == 1

    def test_delete_missing_returns_false(self):
        """Test delete returns False for nonexistent ID."""
        manager = TaskManager()

        result = manager.delete(99)
        assert result is False

    def test_delete_does_not_reuse_id(self):
        """Test that deleted IDs are not reused."""
        manager = TaskManager()
        manager.add("Task 1")
        manager.add("Task 2")
        manager.delete(2)

        task3 = manager.add("Task 3")
        assert task3.id == 3  # Not 2


class TestTaskManagerToggleComplete:
    """Tests for TaskManager.toggle_complete method."""

    def test_toggle_pending_to_complete(self):
        """Test toggling pending task to complete."""
        manager = TaskManager()
        manager.add("Task")

        result = manager.toggle_complete(1)

        assert result is True
        assert manager.get(1).completed is True

    def test_toggle_complete_to_pending(self):
        """Test toggling complete task to pending."""
        manager = TaskManager()
        task = manager.add("Task")
        task.completed = True

        result = manager.toggle_complete(1)

        assert result is True
        assert manager.get(1).completed is False

    def test_toggle_sets_updated_at(self):
        """Test that toggle sets updated_at timestamp."""
        manager = TaskManager()
        manager.add("Task")

        before = datetime.now()
        manager.toggle_complete(1)
        after = datetime.now()

        task = manager.get(1)
        assert task.updated_at is not None
        assert before <= task.updated_at <= after

    def test_toggle_missing_returns_false(self):
        """Test toggle returns False for nonexistent ID."""
        manager = TaskManager()

        result = manager.toggle_complete(99)
        assert result is False


class TestTaskManagerHelpers:
    """Tests for TaskManager helper methods."""

    def test_get_ids_empty(self):
        """Test get_ids returns empty set when no tasks."""
        manager = TaskManager()
        assert manager.get_ids() == set()

    def test_get_ids_returns_all(self):
        """Test get_ids returns all task IDs."""
        manager = TaskManager()
        manager.add("Task 1")
        manager.add("Task 2")
        manager.add("Task 3")

        assert manager.get_ids() == {1, 2, 3}

    def test_get_stats_empty(self):
        """Test get_stats with no tasks."""
        manager = TaskManager()
        stats = manager.get_stats()

        assert stats["total"] == 0
        assert stats["completed"] == 0
        assert stats["pending"] == 0

    def test_get_stats_mixed(self):
        """Test get_stats with mixed tasks."""
        manager = TaskManager()
        manager.add("Task 1")
        manager.add("Task 2")
        manager.add("Task 3")
        manager.toggle_complete(1)

        stats = manager.get_stats()

        assert stats["total"] == 3
        assert stats["completed"] == 1
        assert stats["pending"] == 2

    def test_is_empty_true(self):
        """Test is_empty returns True when no tasks."""
        manager = TaskManager()
        assert manager.is_empty() is True

    def test_is_empty_false(self):
        """Test is_empty returns False when tasks exist."""
        manager = TaskManager()
        manager.add("Task")
        assert manager.is_empty() is False
