"""Tests for UI formatting functions."""

import pytest
from datetime import datetime

from todo.models import Task
from todo.ui import (
    truncate,
    format_datetime,
    format_task_brief,
    format_task_full,
    format_task_detail,
)


class TestTruncate:
    """Tests for truncate function."""

    def test_short_text_unchanged(self):
        """Test that short text is not truncated."""
        result = truncate("Hello", 10)
        assert result == "Hello"

    def test_exact_length_unchanged(self):
        """Test that text at exact length is not truncated."""
        result = truncate("Hello", 5)
        assert result == "Hello"

    def test_long_text_truncated(self):
        """Test that long text is truncated with ellipsis."""
        result = truncate("Hello World", 8)
        assert result == "Hello..."

    def test_default_max_length(self):
        """Test default max length of 50."""
        text = "a" * 60
        result = truncate(text)
        assert len(result) == 50
        assert result.endswith("...")


class TestFormatDatetime:
    """Tests for format_datetime function."""

    def test_formats_correctly(self):
        """Test datetime formatting."""
        dt = datetime(2024, 1, 15, 10, 30, 45)
        result = format_datetime(dt)
        assert result == "2024-01-15 10:30"


class TestFormatTaskBrief:
    """Tests for format_task_brief function."""

    def test_pending_task(self):
        """Test formatting a pending task."""
        task = Task(id=1, title="Buy groceries", completed=False)
        result = format_task_brief(task)
        assert result == "  #1: Buy groceries [pending]"

    def test_completed_task(self):
        """Test formatting a completed task."""
        task = Task(id=2, title="Call mom", completed=True)
        result = format_task_brief(task)
        assert result == "  #2: Call mom [completed]"


class TestFormatTaskFull:
    """Tests for format_task_full function."""

    def test_pending_task_no_description(self):
        """Test formatting a pending task without description."""
        task = Task(
            id=1,
            title="Buy groceries",
            completed=False,
            created_at=datetime(2024, 1, 15, 10, 30),
        )
        result = format_task_full(task)

        assert "[ ] #1: Buy groceries" in result
        assert "Created: 2024-01-15 10:30" in result

    def test_completed_task_with_description(self):
        """Test formatting a completed task with description."""
        task = Task(
            id=2,
            title="Call mom",
            description="Ask about birthday plans",
            completed=True,
            created_at=datetime(2024, 1, 15, 10, 30),
        )
        result = format_task_full(task)

        assert "[x] #2: Call mom" in result
        assert "Ask about birthday plans" in result

    def test_long_description_truncated(self):
        """Test that long descriptions are truncated."""
        task = Task(
            id=1,
            title="Task",
            description="a" * 100,
            created_at=datetime(2024, 1, 15, 10, 30),
        )
        result = format_task_full(task)

        # Should be truncated to 50 chars + ...
        assert "..." in result


class TestFormatTaskDetail:
    """Tests for format_task_detail function."""

    def test_pending_task(self):
        """Test formatting a pending task detail."""
        task = Task(
            id=1,
            title="Buy groceries",
            description="Get milk",
            completed=False,
            created_at=datetime(2024, 1, 15, 10, 30),
        )
        result = format_task_detail(task)

        assert "#1: Buy groceries" in result
        assert "Description: Get milk" in result
        assert "Status: Pending" in result
        assert "Created: 2024-01-15 10:30" in result

    def test_completed_task(self):
        """Test formatting a completed task detail."""
        task = Task(
            id=1,
            title="Task",
            description="",
            completed=True,
            created_at=datetime(2024, 1, 15, 10, 30),
        )
        result = format_task_detail(task)

        assert "Status: Completed" in result

    def test_no_description(self):
        """Test formatting task with no description."""
        task = Task(
            id=1,
            title="Task",
            description="",
            completed=False,
            created_at=datetime(2024, 1, 15, 10, 30),
        )
        result = format_task_detail(task)

        assert "Description: (none)" in result
